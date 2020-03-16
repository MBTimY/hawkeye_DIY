import datetime
import os
import re
import random
import requests
import smtplib
import time
from ipaddress import ip_address
import tldextract
from github import Github
from huey import RedisHuey, crontab
from pymongo import errors, DESCENDING, ASCENDING
from config.database import result_col, query_col, blacklist_col, notice_col, github_col, setting_col, REDIS_HOST, \
    REDIS_PORT, Gitee
from utils.date import timestamp
from utils.log import logger
from utils.notice import mail_notice

huey = RedisHuey('hawkeye', host=REDIS_HOST, port=int(REDIS_PORT))
base_path = os.path.split(os.path.realpath(__file__))[0]
extract = tldextract.TLDExtract(cache_file='{}/.tld_set'.format(base_path))

if setting_col.count({'key': 'task', 'minute': {'$exists': True}, 'page': {'$exists': True}}):
    minute = int(setting_col.find_one({'key': 'task'}).get('minute'))
    setting_col.update_one({'key': 'task'}, {'$set': {'key': 'task', 'pid': os.getpid(), 'last': timestamp()}},
                           upsert=True)

else:
    minute = 10
    setting_col.update_one({'key': 'task'},
                           {'$set': {'key': 'task', 'pid': os.getpid(), 'minute': 10, 'page': 3, 'last': timestamp()}},
                           upsert=True)


@huey.task()
def search(query, page, g, github_username):
    mail_notice_list = []
    webhook_notice_list = []
    logger.info('开始抓取: tag is {} keyword is {}, page is {}'.format(
        query.get('tag'), query.get('keyword'), page + 1))
    try:
        repos = g.search_code(query=query.get('keyword'),
                              sort="indexed", order="desc")
        github_col.update_one({'username': github_username},
                              {'$set': {'rate_remaining': int(g.get_rate_limit().search.remaining)}})

    except Exception as error:
        logger.critical(error)
        logger.critical("触发限制啦")
        return
    try:
        for repo in repos.get_page(page):
            setting_col.update_one({'key': 'task'}, {'$set': {'key': 'task', 'pid': os.getpid(), 'last': timestamp()}},
                                   upsert=True)
            if not result_col.count({'_id': repo.sha}):
                try:
                    code = str(repo.content).replace('\n', '')
                except:
                    code = ''
                leakage = {
                    'link': repo.html_url,
                    'project': repo.repository.full_name,
                    'project_url': repo.repository.html_url,
                    '_id': repo.sha,
                    'language': repo.repository.language,
                    'username': repo.repository.owner.login,
                    'avatar_url': repo.repository.owner.avatar_url,
                    'filepath': repo.path,
                    'filename': repo.name,
                    'security': 0,
                    'ignore': 0,
                    'tag': query.get('tag'),
                    'code': code,
                }
                try:
                    leakage['affect'] = get_affect_assets(repo.decoded_content)
                except Exception as error:
                    logger.critical('{} {}'.format(error, leakage.get('link')))
                    leakage['affect'] = []
                if int(repo.raw_headers.get('x-ratelimit-remaining')) == 0:
                    logger.critical('剩余使用次数: {}'.format(
                        repo.raw_headers.get('x-ratelimit-remaining')))
                    return
                last_modified = datetime.datetime.strptime(
                    repo.last_modified, '%a, %d %b %Y %H:%M:%S %Z')
                leakage['datetime'] = last_modified
                leakage['timestamp'] = last_modified.timestamp()
                in_blacklist = False
                for blacklist in blacklist_col.find({}):
                    if blacklist.get('text').lower() in leakage.get('link').lower():
                        logger.warning('{} 包含白名单中的 {}'.format(
                            leakage.get('link'), blacklist.get('text')))
                        in_blacklist = True
                if in_blacklist:
                    continue
                if result_col.count({"project": leakage.get('project'), "ignore": 1}):
                    continue
                if not result_col.count(
                        {"project": leakage.get('project'), "filepath": leakage.get("filepath"), "security": 0}):
                    mail_notice_list.append(
                        '上传时间:{} 地址: <a href={}>{}/{}</a>'.format(leakage.get('datetime'), leakage.get('link'),
                                                                  leakage.get('project'), leakage.get('filename')))
                    webhook_notice_list.append(
                        '[{}/{}]({}) 上传于 {}'.format(leakage.get('project').split('.')[-1],
                                                    leakage.get('filename'), leakage.get('link'),
                                                    leakage.get('datetime')))
                try:
                    result_col.insert_one(leakage)
                    # logger.info(leakage.get('project'))
                except errors.DuplicateKeyError:
                    logger.info('已存在')

                logger.info('抓取关键字：{} {}'.format(query.get('tag'), leakage.get('link')))
    except Exception as error:
        if 'Not Found' not in error.data:
            g, github_username = new_github()
            search.schedule(
                args=(query, page, g, github_username),
                delay=huey.pending_count() + huey.scheduled_count())
        logger.critical(error)
        logger.error('抓取: tag is {} keyword is {}, page is {} 失败'.format(
            query.get('tag'), query.get('keyword'), page + 1))

        return
    logger.info('抓取: tag is {} keyword is {}, page is {} 成功'.format(
        query.get('tag'), query.get('keyword'), page + 1))
    query_col.update_one({'tag': query.get('tag')},
                         {'$set': {'last': int(time.time()), 'status': 1, 'reason': '抓取第{}页成功'.format(page),
                                   'api_total': repos.totalCount,
                                   'found_total': result_col.count({'tag': query.get('tag')})}})
    if setting_col.count({'key': 'mail', 'enabled': True}) and len(mail_notice_list):
        main_content = '<h2>规则名称: {}</h2><br>{}'.format(query.get('tag'), '<br>'.join(mail_notice_list))
        send_mail(main_content)
    logger.info(len(webhook_notice_list))
    webhook_notice(query.get('tag'), webhook_notice_list)


@huey.task()
def webhook_notice(tag, results):
    if len(results):
        for webhook_setting in setting_col.find({'webhook': {'$exists': True}, 'enabled': True},
                                                {'domain': 1, 'webhook': 1, '_id': 0}):
            hostname = webhook_setting.get('domain')
            webhook = webhook_setting.get('webhook')
            if 'oapi.dingtalk.com' in webhook:
                content = {
                    "msgtype": "markdown",
                    "markdown": {"title": "泄露信息来了",
                                 "text": '#### [规则名称: {}]({}/?tag={})\n\n- {}'.format(tag, hostname, tag,
                                                                                      '\n- '.join(results))
                                 },
                    "at": {
                        "atMobiles": [

                        ],
                        "isAtAll": False
                    }
                }
            else:

                content = {
                    "msgtype": "markdown",
                    "markdown": {
                        "content": '#### [规则名称: {}]({}/?tag={})\n\n- {}'.format(tag, hostname, tag,
                                                                                '\n- '.join(results))
                    }
                }
            try:
                requests.post(
                    webhook,
                    json=content)
            except Exception as error:
                logger.error(error)


def get_domain(target):
    result = extract(target)
    if bool(len(result.suffix)) and bool(len(result.domain)):
        return '{}.{}'.format(result.domain, result.suffix)
    else:
        return False


def get_affect_assets(code):
    """

    :param code:
    :return:
    """
    code = str(code)
    affect = []
    domain_pattern = '(?!\-)(?:[a-zA-Z\d\-]{0,62}[a-zA-Z\d]\.){1,126}(?!\d+)[a-zA-Z\d]{1,63}'
    ip_pattern = "(\d+\.\d+\.\d+\.\d+)"
    email_pattern = "[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?"
    affect_assets = {
        'domain': list(set(re.findall(domain_pattern, code))),
        'email': list(set(re.findall(email_pattern, code))),
        'ip': list(set(re.findall(ip_pattern, code))),
    }
    for assets in affect_assets.keys():
        if len(affect_assets.get(assets)) > 100:
            affect_assets[assets] = []
            continue
        for asset in affect_assets.get(assets):
            if assets == 'ip':
                if not is_ip(asset):
                    continue
            if assets == 'domain':
                if not get_domain(asset):
                    continue
            if assets == 'email':
                if not get_domain(asset.split('@')[-1]):
                    continue
            affect.append({'type': assets, 'value': asset.replace(
                "'", "").replace('"', '').replace("`", "").lower()})
    return affect


def is_ip(ip):
    """

    :param ip:
    :return:
    """
    try:
        ip_address(ip)
        return True
    except ValueError:
        return False


@huey.task()
def send_mail(content):
    smtp_config = setting_col.find_one({'key': 'mail'})
    receivers = [data.get('mail') for data in notice_col.find({})]
    try:
        if mail_notice(smtp_config, receivers, content):
            logger.info('邮件发送成功')
        else:
            logger.critical('Error: 无法发送邮件')

    except smtplib.SMTPException as error:
        logger.critical('Error: 无法发送邮件 {}'.format(error))


@huey.periodic_task(crontab(minute='*/2'))
def update_rate_remain():
    for account in github_col.find():
        github_username = account.get('username')
        github_password = account.get('password')
        try:
            g = Github(github_username, github_password)
            github_col.update_one({'username': github_username},
                                  {'$set': {'rate_remaining': int(g.get_rate_limit().search.remaining),
                                            'rate_limit': int(g.get_rate_limit().search.limit)}})
        except Exception as error:
            logger.error(error)


def new_github():
    if github_col.count({'rate_remaining': {'$gt': 5}}):
        pass
    else:
        logger.error('请配置github账号')
        return
    github_account = random.choice(list(github_col.find({"rate_limit": {"$gt": 5}}).sort('rate_remaining', DESCENDING)))
    github_username = github_account.get('username')
    github_password = github_account.get('password')
    g = Github(github_username, github_password)
    return g, github_username


@huey.periodic_task(crontab(minute='*/{}'.format(minute)))
def check():
    setting_col.update_one({'key': 'task'}, {'$set': {'key': 'task', 'pid': os.getpid()}}, upsert=True)
    query_count = query_col.count({'enabled': True})
    logger.info('需要处理的关键词总数: {}'.format(query_count))
    if query_count:
        logger.info('需要处理的关键词总数: {}'.format(query_count))
    else:
        logger.warning('请添加关键词')
        return
    if github_col.count({'rate_remaining': {'$gt': 5}}):
        pass
    else:
        logger.error('请配置github账号')
        return

    if setting_col.count({'key': 'task', 'page': {'$exists': True}}):
        setting_col.update_one({'key': 'task'}, {'$set': {'pid': os.getpid()}})
        page = int(setting_col.find_one({'key': 'task'}).get('page'))
        for p in range(0, page):
            for query in query_col.find({'enabled': True}).sort('last', ASCENDING):
                github_account = random.choice(
                    list(github_col.find({"rate_limit": {"$gt": 5}}).sort('rate_remaining', DESCENDING)))
                github_username = github_account.get('username')
                github_password = github_account.get('password')
                rate_remaining = github_account.get('rate_remaining')
                logger.info(github_username)
                logger.info(rate_remaining)
                g = Github(github_username, github_password,
                           user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36')
                # 码云爬取任务
                crawl.schedule(args=(query, p), delay=huey.pending_count() + huey.scheduled_count())
                # Github爬取任务
                search.schedule(args=(query, p, g, github_username),
                                delay=huey.pending_count() + huey.scheduled_count())
    else:
        logger.error('请在页面上配置任务参数')

# 码云-------
from datetime import date
from lxml import etree
import hashlib
import base64

def _md5(data):
    m = hashlib.md5()
    m.update(data.encode('utf-8'))
    result = m.hexdigest()
    return result

def _format_time(time_string):
    if isinstance(time_string, str):
        t = datetime.datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S')
    elif isinstance(time_string, date):
        t = time_string
    return  t

def gitee_login():
    username = Gitee.USERNAME
    pwd = Gitee.PASSWORD
    session = requests.session()
    login_url = 'https://gitee.com/login'
    authenticity_token = re.findall('name="authenticity_token".*?value="(.*?)" />',
                                 session.get(login_url).text)[0]
    post_form = {
        'utf8': '✓',
        'user[login]': username,
        'user[password]':pwd,
        'user[remember_me]':0,
        'commit': u'登 录',
        'authenticity_token': authenticity_token,
    }
    session.post(login_url, data=post_form)
    return session

def gitee_raw_code(code_url):
    try:
        resp = requests.get(code_url.replace("/blob/","/raw/"))
        return resp.text.encode(resp.encoding).decode('utf-8')
    except Exception as e:
        print(code_url,'get gitee raw code error')
        return None

cut_tail = lambda url: url[0:url.rindex('?_from')]

@huey.task()
def crawl(query, page):
    mail_notice_list = []
    webhook_notice_list = []
    search_url = 'https://search.gitee.com/?skin=rec&type=code&q={1}&sort=last_indexed' \
                 '&pageno={0}'
    session = gitee_login()

    logger.info('Gitee开始抓取: tag is {} keyword is {}, page is {}'.format(
        query.get('tag'), query.get('keyword'), page + 1))
    totalCount = 0
    for page in range(page+1, page+2):
        try:
            logger.info("Gitee ------ 启动抓取: {}".format(search_url.format(page,query.get('keyword'))))
            resp = session.get(search_url.format(page,query.get('keyword')))
            logger.info("Gitee 启动抓取: {}".format(search_url.format(page,query.get('keyword'))))
            tree = etree.HTML(resp.text)
            nodes = tree.xpath('//*[@id="hits-list"]/div[@class="item"]')
            for node in nodes:
                logger.info("Gitee 开始抓取节点")
                totalCount += 1
                # i = nodes.index(node) + 1
                leakage = {}
                leakage['affect'] = []
                datetime_ = node.xpath(Gitee.DATETIME)[0].text
                # print(datetime)
                datetime_match = re.match("[^\d]*(?P<Date>\d+.*)", datetime_)
                if not datetime_match:
                    leakage['datetime'] = _format_time(datetime.datetime.now().date())
                else:
                    leakage['datetime'] = _format_time(datetime_match.groups("Date")[0])
                leakage['timestamp'] = leakage.get('datetime').timestamp()
                leakage['link'] = cut_tail(node.xpath(Gitee.LINK)[0].attrib['href'])
                leakage['filepath'] = node.xpath(Gitee.LINK)[0].text
                leakage['filename'] = leakage.get("filepath").split("/")[-1]
                # leakage['link'] = 'https://gitee.com' + realative_link
                leakage['_id'] = _md5(leakage['link'])
                logger.info("Gitee ****** 开始抓取节点 {}".format(leakage['datetime']))
                project_username =  node.xpath(Gitee.USERNAME)[0].text
                leakage["vendor"] = "GITEE"
                leakage['username'] = project_username.split("/")[0]
                leakage['project'] = project_username
                leakage['project_url'] = cut_tail(node.xpath(Gitee.USERNAME)[0].attrib['href'])
                logger.info("Gitee 抓取到 {}".format(leakage.get("project_url")))

                if result_col.find_one({"link": leakage['link'], "datetime": leakage['datetime']}) or \
                        result_col.find_one({'_id': leakage['_id']}):
                    continue

                in_blacklist = False
                for blacklist in blacklist_col.find({}):
                    if blacklist.get('text').lower() in leakage.get('link').lower():
                        logger.warning('{} 包含白名单中的 {}'.format(
                            leakage.get('link'), blacklist.get('text')))
                        in_blacklist = True
                if in_blacklist:
                    continue

                if result_col.count({"project": leakage.get('project'), "ignore": 1}):
                    continue

                #gitee中可以只有项目，没有代码
                leakage['avatar_url'] = 'https://gitee.com/logo-black.svg'
                raw_code = gitee_raw_code(leakage['link'])
                leakage['code'] = base64.b64encode(raw_code.encode("utf-8")).decode("utf-8")
                try:
                    leakage['affect'] = get_affect_assets(raw_code)
                except Exception as error:
                    logger.critical('{} {}'.format(error, leakage.get('link')))
                    leakage['affect'] = []
                leakage['tag'] = query['tag']
                # leakage['detail'] = etree.tostring(node,encoding='unicode').replace('{{', '<<').\
                    # replace('}}', '>>')
                language_node = node.xpath(Gitee.LANGUAGE)
                if language_node:
                    leakage['language'] = language_node[0].text.strip()
                else:
                    leakage['language'] = 'Unknow'
                leakage['security'] = 0
                leakage['ignore'] = 0

                if not result_col.count(
                        {"project": leakage.get('project'), "filepath": leakage.get("filepath"), "security": 0}):
                    mail_notice_list.append(
                        '上传时间:{} 地址: <a href={}>{}/{}</a>'.format(leakage.get('datetime'), leakage.get('link'),
                                                                  leakage.get('project'), leakage.get('filename')))
                    webhook_notice_list.append(
                        '[{}/{}]({}) 上传于 {}'.format(leakage.get('project').split('/')[-1],
                                                    leakage.get('filename'), leakage.get('link'),
                                                    leakage.get('datetime')))

                result_col.insert_one(leakage)
                logger.info("Gitee 抓取到的结果: {}".format(leakage.get("project_url")))
        except Exception as e:
            raise(e)
            print(e)
            logger.error("Gitee error is {}".format(e))
            return
        logger.info('Gitee抓取: tag is {} keyword is {}, page is {} 成功'.format(
        query.get('tag'), query.get('keyword'), page + 1))
        query_col.update_one({'tag': query.get('tag')},
                         {'$set': {'last': int(time.time()), 'status': 1, 'reason': '抓取第{}页成功'.format(page),
                                   'api_total': totalCount,
                                   'found_total': result_col.count({'tag': query.get('tag')})}})
        if setting_col.count({'key': 'mail', 'enabled': True}) and len(mail_notice_list):
            main_content = '<h2>规则名称: {}</h2><br>{}'.format(query.get('tag'), '<br>'.join(mail_notice_list))
            send_mail(main_content)
        logger.info(len(webhook_notice_list))
        webhook_notice(query.get('tag'), webhook_notice_list)                                

(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-4d2de4b7"],{8418:function(e,t,r){"use strict";var n=r("c04e"),o=r("9bf2"),a=r("5c6c");e.exports=function(e,t,r){var i=n(t);i in e?o.f(e,i,a(0,r)):e[i]=r}},"99af":function(e,t,r){"use strict";var n=r("23e7"),o=r("d039"),a=r("e8b5"),i=r("861d"),l=r("7b0b"),s=r("50c4"),c=r("8418"),u=r("65f0"),d=r("1dde"),f=r("b622"),m=r("2d00"),b=f("isConcatSpreadable"),p=9007199254740991,h="Maximum allowed index exceeded",g=m>=51||!o((function(){var e=[];return e[b]=!1,e.concat()[0]!==e})),w=d("concat"),v=function(e){if(!i(e))return!1;var t=e[b];return void 0!==t?!!t:a(e)},y=!g||!w;n({target:"Array",proto:!0,forced:y},{concat:function(e){var t,r,n,o,a,i=l(this),d=u(i,0),f=0;for(t=-1,n=arguments.length;t<n;t++)if(a=-1===t?i:arguments[t],v(a)){if(o=s(a.length),f+o>p)throw TypeError(h);for(r=0;r<o;r++,f++)r in a&&c(d,f,a[r])}else{if(f>=p)throw TypeError(h);c(d,f++,a)}return d.length=f,d}})},f2b9:function(e,t,r){"use strict";r.r(t);var n=function(){var e=this,t=e.$createElement,r=e._self._c||t;return r("div",{staticClass:"setting-card"},[r("el-dialog",{attrs:{title:"添加监控项",visible:e.dialogFormVisible,width:e.mobileClient?"80%":"50%"},on:{"update:visible":function(t){e.dialogFormVisible=t}},model:{value:e.dialogFormVisible,callback:function(t){e.dialogFormVisible=t},expression:"dialogFormVisible"}},[r("el-form",{attrs:{model:e.form}},[r("el-form-item",{attrs:{label:"名称"}},[r("el-popover",{attrs:{placement:"right",title:"提示",width:"200",trigger:"hover"}},[e._v("若存在相同名称，会覆盖已有值\n                    "),r("i",{staticClass:"el-icon-question",attrs:{slot:"reference"},slot:"reference"})]),r("el-input",{attrs:{"auto-complete":"off"},model:{value:e.form.tag,callback:function(t){e.$set(e.form,"tag",t)},expression:"form.tag"}})],1),r("el-form-item",{attrs:{label:"关键字"}},[r("el-popover",{attrs:{placement:"right",title:"提示",width:"200",trigger:"hover"}},[e._v("熟悉\n                    "),r("a",{attrs:{referrerpolicy:"no-referrer",href:"https://github.com/search/advanced",target:"_blank"}},[e._v("GitHub 搜索语法")]),e._v("可以提高监控效率: OR/AND/NOT\n                    "),r("i",{staticClass:"el-icon-question",attrs:{slot:"reference"},slot:"reference"})]),r("el-input",{attrs:{"auto-complete":"off"},model:{value:e.form.keyword,callback:function(t){e.$set(e.form,"keyword",t)},expression:"form.keyword"}})],1),r("el-form-item",{attrs:{label:"开启/关闭"}},[r("el-switch",{attrs:{"active-color":"#13ce66","inactive-color":"#ff4949"},model:{value:e.form.enabled,callback:function(t){e.$set(e.form,"enabled",t)},expression:"form.enabled"}})],1)],1),r("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[r("el-button",{attrs:{round:"",size:"mini"},on:{click:function(t){e.dialogFormVisible=!1}}},[e._v("取 消")]),r("el-button",{attrs:{round:"",size:"mini",type:"primary"},on:{click:function(t){return e.handleAddQuery(e.form)}}},[e._v("确 定")])],1)],1),r("el-button",{attrs:{type:"primary",size:"mini"},on:{click:function(t){e.dialogFormVisible=!0}}},[e._v("\n        添加\n    ")]),r("el-table",{attrs:{data:e.rules,stripe:!0}},[r("el-table-column",{attrs:{label:"名称"},scopedSlots:e._u([{key:"default",fn:function(t){return[r("router-link",{attrs:{to:"/?tag="+t.row.tag}},[e._v("\n                    "+e._s(t.row.tag)+"\n                ")])]}}])}),r("el-table-column",{attrs:{label:"关键字","show-overflow-tooltip":""},scopedSlots:e._u([{key:"default",fn:function(t){return[r("a",{attrs:{rel:"noopener noreferrer",href:"https://github.com/search?o=desc&q="+t.row.keyword+"&ref=searchresults&s=indexed&type=Code&utf8=%E2%9C%93",target:"_blank"}},[e._v(e._s(t.row.keyword))])]}}])}),r("el-table-column",{attrs:{label:"最后抓取时间",prop:"last",width:"150",sortable:""},scopedSlots:e._u([{key:"default",fn:function(t){return[t.row.last?r("span",[e._v(e._s(e._f("timeAgo")(1e3*t.row.last)))]):e._e()]}}])}),r("el-table-column",{attrs:{label:"总数",width:"200",prop:"api_total",sortable:""}}),r("el-table-column",{attrs:{label:"已抓取",width:"200",prop:"found_total",sortable:""}}),r("el-table-column",{attrs:{label:"状态",width:"100",prop:"enabled",sortable:""},scopedSlots:e._u([{key:"default",fn:function(t){return[r("el-switch",{attrs:{"active-color":"#13ce66","inactive-color":"#ff4949"},on:{change:function(r){return e.updateEnabled(t.row)}},model:{value:t.row.enabled,callback:function(r){e.$set(t.row,"enabled",r)},expression:"scope.row.enabled"}})]}}])}),r("el-table-column",{attrs:{label:"操作",width:"200"},scopedSlots:e._u([{key:"default",fn:function(t){return[r("el-button-group",[r("el-button",{attrs:{size:"mini",plain:"",round:""},on:{click:function(r){return e.handleEdit(t.$index,t.row)}}},[e._v("编辑\n                    ")]),r("el-button",{attrs:{size:"mini",type:"danger",plain:""},on:{click:function(r){return e.handleDeleteQuery(t.$index,t.row)}}},[e._v("删除\n                    ")]),0===t.row.status?r("el-button",{attrs:{size:"mini",plain:"",round:"",type:"primary",icon:"el-icon-loading"},on:{click:function(r){return e.handleSpiderResult(t.row)}}}):e._e(),1===t.row.status?r("el-button",{attrs:{size:"mini",type:"success",plain:"",round:"",icon:"el-icon-success"},on:{click:function(r){return e.handleSpiderResult(t.row)}}}):e._e(),-1===t.row.status?r("el-button",{attrs:{size:"mini",type:"warning",plain:"",round:"",icon:"el-icon-warning"},on:{click:function(r){return e.handleSpiderResult(t.row)}}}):e._e()],1)]}}])})],1)],1)},o=[],a=(r("99af"),r("d3b7"),r("25f0"),["second","minute","hour","day","week","month","year"]),i=function(e,t){if(0===t)return["just now","right now"];var r=a[Math.floor(t/2)];return e>1&&(r+="s"),[e+" "+r+" ago","in "+e+" "+r]},l=["秒","分钟","小时","天","周","个月","年"],s=function(e,t){if(0===t)return["刚刚","片刻后"];var r=l[~~(t/2)];return[e+" "+r+"前",e+" "+r+"后"]},c={},u=function(e,t){c[e]=t},d=function(e){return c[e]||c["en_US"]},f=[60,60,24,7,365/7/12,12];function m(e){return e instanceof Date?e:!isNaN(e)||/^\d+$/.test(e)?new Date(parseInt(e)):(e=(e||"").trim().replace(/\.\d+/,"").replace(/-/,"/").replace(/-/,"/").replace(/(\d)T(\d)/,"$1 $2").replace(/Z/," UTC").replace(/([+-]\d\d):?(\d\d)/," $1$2"),new Date(e))}function b(e,t){var r=e<0?1:0;e=Math.abs(e);for(var n=e,o=0;e>=f[o]&&o<f.length;o++)e/=f[o];return e=Math.floor(e),o*=2,e>(0===o?9:1)&&(o+=1),t(e,o,n)[r].replace("%s",e.toString())}function p(e,t){var r=t?m(t):new Date;return(+r-+m(e))/1e3}var h=function(e,t,r){var n=p(e,r&&r.relativeDate);return b(n,d(t))};u("en_US",i),u("zh_CN",s);var g={data:function(){return{rules:[],dialogFormVisible:!1,form:{tag:"",keyword:"",enabled:!0}}},computed:{mobileClient:function(){return document.documentElement.clientWidth<document.documentElement.clientHeight}},methods:{handleEdit:function(e,t){this.form=t,this.dialogFormVisible=!0},fetchQuery:function(){var e=this;this.axios.get(this.api.settingQuery).then((function(t){e.rules=t.data.result})).catch((function(t){e.$message.error(t.toString())}))},handleSpiderResult:function(e){var t=h(1e3*e.last,"zh_CN");e.status>-1?this.$message.success(t+e.reason):this.$message.warning(t+e.reason)},handleDeleteQuery:function(e,t){var r=this;this.axios.delete("".concat(this.api.settingQuery,"?_id=").concat(t._id,"&tag=").concat(t.tag)).then((function(e){r.$message.success(e.data.msg),r.dialogFormVisible=!1,r.rules=e.data.result})).catch((function(e){r.$message.error(e.toString()),r.dialogFormVisible=!1}))},updateEnabled:function(e){var t=this,r={tag:e.tag,keyword:e.keyword,enabled:e.enabled};this.axios.post(this.api.settingQuery,r).then((function(e){t.$message.success(e.data.msg),t.dialogFormVisible=!1,t.rules=e.data.result})).catch((function(e){t.$message.error(e.toString()),t.dialogFormVisible=!1}))},handleAddQuery:function(e){var t=this;this.axios.post(this.api.settingQuery,e).then((function(e){t.$message.success(e.data.msg),t.dialogFormVisible=!1,t.rules=e.data.result,t.form={tag:"",keyword:"",enabled:!0}})).catch((function(e){t.$message.error(e.toString()),t.dialogFormVisible=!1}))}},mounted:function(){this.fetchQuery()}},w=g,v=r("2877"),y=Object(v["a"])(w,n,o,!1,null,null,null);t["default"]=y.exports}}]);
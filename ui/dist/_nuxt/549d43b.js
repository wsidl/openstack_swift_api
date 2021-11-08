(window.webpackJsonp=window.webpackJsonp||[]).push([[0],{162:function(t,e,n){"use strict";var c={data:function(){return{}}},o=n(37),component=Object(o.a)(c,(function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("div",[t._m(0),t._v(" "),n("section",{staticClass:"section main-content"},[n("Nuxt")],1)])}),[function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("section",{staticClass:"hero is-primary"},[n("div",{staticClass:"hero-body"},[n("h1",{staticClass:"title"},[t._v("Object Store App")]),t._v(" "),n("h2",{staticClass:"subtitle"},[t._v("Simple Object Store Catalogue")])])])}],!1,null,null,null);e.a=component.exports},167:function(t,e,n){n(168),t.exports=n(169)},213:function(t,e,n){"use strict";n.r(e),n.d(e,"state",(function(){return c})),n.d(e,"getters",(function(){return o})),n.d(e,"mutations",(function(){return r})),n.d(e,"actions",(function(){return f}));n(214),n(215),n(155),n(30),n(13),n(64);var c=function(){return{objects:[]}},o={getObject:function(t){return function(e){return t.objects.find((function(t){return t.id===e}))}}},r={addObjects:function(t,e){t.objects=e},setTag:function(t,e){var n=e.object_id,c=e.tagName,o=e.tagValue;t.objects.find((function(t){return t.id===n})).metadata.push([c,o])},deleteTag:function(t,e){var n=e.object_id,c=e.tagName,o=e.tagValue,r=t.objects.find((function(t){return t.id===n})),f=r.metadata.findIndex((function(t){return t[0]===c&&t[1]===o}));f>-1&&r.metadata.splice(f,1)},saveName:function(t,e){var n=e.object_id,c=e.name;t.objects.find((function(t){return t.id===n})).name=c},deleteObject:function(t,e){t.objects.splice(t.objects.findIndex((function(t){return t.id===e})),1)}},f={getObjects:function(t){var e=t.commit;fetch("obj").then((function(t){return t.json()})).then((function(t){if("success"===t.status)return t.content;throw new Error(t.message)})).then((function(t){return e("addObjects",t)})).catch((function(t){return console.error(t)}))},setTag:function(t,e){var n=t.commit,c=e.object_id,o=e.tagName,r=e.tagValue;fetch("obj/".concat(c,"/tag/").concat(o,"/").concat(r),{method:"PUT"}).then((function(){n("setTag",{object_id:c,tagName:o,tagValue:r})})).catch((function(t){return console.error("Tag ".concat(o," errored on add"),t)}))},deleteTag:function(t,e){var n=t.commit,c=e.object_id,o=e.tagName,r=e.tagValue;fetch("obj/".concat(c,"/tag/").concat(o,"/").concat(r),{method:"DELETE"}).then((function(){n("deleteTag",{object_id:c,tagName:o,tagValue:r})})).catch((function(t){return console.error("Tag ".concat(o," errored on delete"),t)}))},saveName:function(t,e){t.commit;var n=t.dispatch,c=e.object_id,o=e.name;fetch("obj/".concat(c,"/name/").concat(o),{method:"POST"}).then((function(){n("getObjects")}))},deleteObject:function(t,e){var n=t.dispatch,c=e.object_id;return fetch("obj/".concat(c),{method:"DELETE"}).then((function(){n("getObjects")}))},newObject:function(t,e){t.commit;var n=t.dispatch,c=e.fileData,o=e.name,r=e.tags,form=new FormData;form.append("name",o),form.append("file",c),form.append("tags",JSON.stringify(r)),fetch("obj",{method:"PUT",body:form}).then((function(t){if(!1===t.ok)throw new Error(t.statusText);return t.json()})).then((function(t){if("error"===t.status)throw new Error(t.message);return n("getObjects"),t.content})).catch((function(t){return console.error(t)}))}}}},[[167,6,1,7]]]);
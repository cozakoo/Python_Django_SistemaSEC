!/**
 * Highstock JS v11.4.1 (2024-04-04)
 *
 * Slow Stochastic series type for Highcharts Stock
 *
 * (c) 2010-2024 Pawel Fus
 *
 * License: www.highcharts.com/license
 */function(t){"object"==typeof module&&module.exports?(t.default=t,module.exports=t):"function"==typeof define&&define.amd?define("highcharts/indicators/indicators",["highcharts","highcharts/modules/stock"],function(e){return t(e),t.Highcharts=e,t}):t("undefined"!=typeof Highcharts?Highcharts:void 0)}(function(t){"use strict";var e=t?t._modules:{};function o(t,e,o,a){t.hasOwnProperty(e)||(t[e]=a.apply(null,o),"function"==typeof CustomEvent&&window.dispatchEvent(new CustomEvent("HighchartsModuleLoaded",{detail:{path:e,module:t[e]}})))}o(e,"Stock/Indicators/SlowStochastic/SlowStochasticIndicator.js",[e["Core/Series/SeriesRegistry.js"],e["Core/Utilities.js"]],function(t,e){var o,a=this&&this.__extends||(o=function(t,e){return(o=Object.setPrototypeOf||({__proto__:[]})instanceof Array&&function(t,e){t.__proto__=e}||function(t,e){for(var o in e)Object.prototype.hasOwnProperty.call(e,o)&&(t[o]=e[o])})(t,e)},function(t,e){if("function"!=typeof e&&null!==e)throw TypeError("Class extends value "+String(e)+" is not a constructor or null");function a(){this.constructor=t}o(t,e),t.prototype=null===e?Object.create(e):(a.prototype=e.prototype,new a)}),r=t.seriesTypes,s=r.sma,n=r.stochastic,i=e.extend,c=e.merge,u=function(t){function e(){return null!==t&&t.apply(this,arguments)||this}return a(e,t),e.prototype.getValues=function(e,o){var a=o.periods,r=t.prototype.getValues.call(this,e,o),n={values:[],xData:[],yData:[]};if(r){n.xData=r.xData.slice(a[1]-1);var i=r.yData.slice(a[1]-1),c=s.prototype.getValues.call(this,{xData:n.xData,yData:i},{index:1,period:a[2]});if(c){for(var u=0,l=n.xData.length;u<l;u++)n.yData[u]=[i[u][1],c.yData[u-a[2]+1]||null],n.values[u]=[n.xData[u],i[u][1],c.yData[u-a[2]+1]||null];return n}}},e.defaultOptions=c(n.defaultOptions,{params:{periods:[14,3,3]}}),e}(n);return i(u.prototype,{nameBase:"Slow Stochastic"}),t.registerSeriesType("slowstochastic",u),u}),o(e,"masters/indicators/slow-stochastic.src.js",[e["Core/Globals.js"]],function(t){return t})});
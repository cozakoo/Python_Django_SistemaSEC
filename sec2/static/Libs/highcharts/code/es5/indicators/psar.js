!/**
 * Highstock JS v11.4.1 (2024-04-04)
 *
 * Parabolic SAR Indicator for Highcharts Stock
 *
 * (c) 2010-2024 Grzegorz Blachliński
 *
 * License: www.highcharts.com/license
 */function(t){"object"==typeof module&&module.exports?(t.default=t,module.exports=t):"function"==typeof define&&define.amd?define("highcharts/indicators/psar",["highcharts","highcharts/modules/stock"],function(e){return t(e),t.Highcharts=e,t}):t("undefined"!=typeof Highcharts?Highcharts:void 0)}(function(t){"use strict";var e=t?t._modules:{};function n(t,e,n,o){t.hasOwnProperty(e)||(t[e]=o.apply(null,n),"function"==typeof CustomEvent&&window.dispatchEvent(new CustomEvent("HighchartsModuleLoaded",{detail:{path:e,module:t[e]}})))}n(e,"Stock/Indicators/PSAR/PSARIndicator.js",[e["Core/Series/SeriesRegistry.js"],e["Core/Utilities.js"]],function(t,e){var n,o=this&&this.__extends||(n=function(t,e){return(n=Object.setPrototypeOf||({__proto__:[]})instanceof Array&&function(t,e){t.__proto__=e}||function(t,e){for(var n in e)Object.prototype.hasOwnProperty.call(e,n)&&(t[n]=e[n])})(t,e)},function(t,e){if("function"!=typeof e&&null!==e)throw TypeError("Class extends value "+String(e)+" is not a constructor or null");function o(){this.constructor=t}n(t,e),t.prototype=null===e?Object.create(e):(o.prototype=e.prototype,new o)}),r=t.seriesTypes.sma,i=e.merge;function a(t,e){return parseFloat(t.toFixed(e))}var s=function(t){function e(){var e=null!==t&&t.apply(this,arguments)||this;return e.nameComponents=void 0,e}return o(e,t),e.prototype.getValues=function(t,e){var n,o,r,i,s,c,l,u,p,h,d,f,m,y,v,g,x,_,j,A,F,O,w,C,M,S=t.xData,b=t.yData,P=e.maxAccelerationFactor,D=e.increment,E=e.initialAccelerationFactor,H=e.decimals,k=e.index,R=[],T=[],I=[],W=e.initialAccelerationFactor,G=b[0][1],L=1,U=b[0][2];if(!(k>=b.length)){for(M=0;M<k;M++)G=Math.max(b[M][1],G),U=Math.min(b[M][2],a(U,H));for(y=b[M][1]>U?1:-1,v=G-U,g=(W=e.initialAccelerationFactor)*v,R.push([S[k],U]),T.push(S[k]),I.push(a(U,H)),M=k+1;M<b.length;M++)_=b[M-1][2],j=b[M-2][2],A=b[M-1][1],F=b[M-2][1],w=b[M][1],C=b[M][2],null!==j&&null!==F&&null!==_&&null!==A&&null!==w&&null!==C&&(n=y,o=L,r=U,i=g,s=G,U=n===o?1===n?r+i<Math.min(j,_)?r+i:Math.min(j,_):r+i>Math.max(F,A)?r+i:Math.max(F,A):s,h=y,d=G,O=1===h?w>d?w:d:C<d?C:d,f=L,m=U,c=x=1===f&&C>m||-1===f&&w>m?1:-1,l=y,u=G,p=W,g=(W=c===l?1===c&&O>u||-1===c&&O<u?p===P?P:a(p+D,2):p:E)*(v=O-U),R.push([S[M],a(U,H)]),T.push(S[M]),I.push(a(U,H)),L=y,y=x,G=O);return{values:R,xData:T,yData:I}}},e.defaultOptions=i(r.defaultOptions,{lineWidth:0,marker:{enabled:!0},states:{hover:{lineWidthPlus:0}},params:{period:void 0,initialAccelerationFactor:.02,maxAccelerationFactor:.2,increment:.02,index:2,decimals:4}}),e}(r);return t.registerSeriesType("psar",s),s}),n(e,"masters/indicators/psar.src.js",[e["Core/Globals.js"]],function(t){return t})});
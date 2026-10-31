/* Diagrams render locally; no third-party CDN or account data is used. */
function renderFridayDiagrams(){
  const nodes=[...document.querySelectorAll('.friday-diagram:not([data-processed])')];
  if(!nodes.length)return;
  mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'neutral',fontFamily:'PingFang SC, Microsoft YaHei, sans-serif'});
  mermaid.run({nodes}).catch(error=>{console.error('Diagram rendering failed',error);});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',renderFridayDiagrams);else renderFridayDiagrams();

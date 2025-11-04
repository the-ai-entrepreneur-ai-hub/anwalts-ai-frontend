(function(){
  function hideEdit(){
    try{
      var nodes=document.querySelectorAll('a,button,[role="button"]');
      for(var i=0;i<nodes.length;i++){
        var el=nodes[i];
        var href=(el.getAttribute && (el.getAttribute('href')||''))||''; href=href.toLowerCase();
        var txt=((el.textContent||'').trim()).toLowerCase();
        if(href.indexOf('framer.link')!==-1){ el.style.display='none'; el.setAttribute('hidden','hidden'); el.setAttribute('aria-hidden','true'); }
        if(txt==='edit alter' || txt==='edit content' || txt==='edit this page' || txt==='bearbeiten' || txt==='seite bearbeiten'){
          el.style.display='none'; el.setAttribute('hidden','hidden'); el.setAttribute('aria-hidden','true');
        }
      }
    }catch(_){/* no-op */}
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', hideEdit); else hideEdit();
  new MutationObserver(function(ms){ for(var k=0;k<ms.length;k++){ var a=ms[k]; if(a.addedNodes){ for(var j=0;j<a.addedNodes.length;j++){ var n=a.addedNodes[j]; if(n&&n.nodeType===1) hideEdit(); } } } }).observe(document.documentElement,{childList:true,subtree:true});
})();

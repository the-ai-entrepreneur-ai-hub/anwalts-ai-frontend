(function(){
  function hide(){
    try{
      var nodes=document.querySelectorAll('a[href*="framer.link"]');
      for(var i=0;i<nodes.length;i++){
        var el=nodes[i];
        // Only hide if it looks like an editor CTA: minimal area, inside known container, or carries Variant 1 name
        var name=(el.getAttribute('data-framer-name')||'').toLowerCase();
        var cls=el.className||'';
        var isVariant = name === 'variant 1';
        var isTiny = (el.offsetWidth && el.offsetWidth < 350) && (el.offsetHeight && el.offsetHeight < 120); // guard against big CTAs
        if (isVariant || el.href.indexOf('Vu5MARe') !== -1) {
          el.style.display='none'; el.setAttribute('hidden','hidden'); el.setAttribute('aria-hidden','true');
        }
      }
    }catch(_){/* no-op */}
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', hide); else hide();
})();

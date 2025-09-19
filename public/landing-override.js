(function(){
  function closestClickable(el){
    while(el && el !== document && !(el.tagName==='A' || el.tagName==='BUTTON')) el = el.parentElement;
    return el;
  }
  function wantsAuth(el){
    try{
      const t=(el.textContent||'').toLowerCase();
      const href=(el.getAttribute&&el.getAttribute('href'))||'';
      const role=(el.getAttribute&&el.getAttribute('role'))||'';
      const da=(el.getAttribute&&el.getAttribute('data-auth'))||'';
      if (da==='login'||da==='register') return true;
      if (/framer\.(link|com|website|cloud)/i.test(href)) return true;
      if (/^login$|^log in$|anmelden|sign\s*in|einloggen/.test(t)) return true;
      if (/^register$|registrieren|sign\s*up|jetzt\s*starten|start\s*now/.test(t)) return true;
      if (role==='link' && /auth|login|register/i.test(t)) return true;
      return false;
    }catch(_){return false}
  }
  function openAuth(){
    try{
      if (typeof window.openAuthModal==='function'){ window.openAuthModal(); return; }
      if (typeof window.showSignInModal==='function'){ window.showSignInModal(); return; }
      window.location.assign('/assistant');
    }catch(_){ try{ window.location.assign('/assistant'); }catch(__){} }
  }
  // Global capture to stop nav
  document.addEventListener('click', function(e){
    try{
      const path=e.composedPath&&e.composedPath();
      let el=(path&&path.length?path[0]:e.target);
      el = closestClickable(el);
      if (!el) return;
      if (wantsAuth(el)) { e.preventDefault(); e.stopPropagation(); openAuth(); }
    }catch(_){ }
  }, true);
  // Also neutralize anchors after load
  (function patch(){
    try{
      document.querySelectorAll('a[href*="framer."]').forEach(function(a){
        a.addEventListener('click', function(ev){ ev.preventDefault(); ev.stopPropagation(); openAuth(); }, {capture:true});
      });
    }catch(_){ }
    try{
      new MutationObserver(function(){
        try{
          document.querySelectorAll('a[href*="framer."]').forEach(function(a){
            a.addEventListener('click', function(ev){ ev.preventDefault(); ev.stopPropagation(); openAuth(); }, {capture:true});
          });
        }catch(_){}
      }).observe(document.documentElement,{subtree:true, childList:true});
    }catch(_){}
  })();
})();

// Proper auth modal integration for Assistant buttons
(function(){
  function openAuth(mode){
    var m = mode || 'login';
    try { console.log('[auth-connector] redirecting to SSR auth:', m); } catch(e){}
    window.location.href = '/dashboard?auth=' + encodeURIComponent(m);
  }
  window.openAuth = openAuth;

  document.addEventListener('DOMContentLoaded', function(){
    // Attach to any CTA-like buttons/links
    var selectors = ['[data-framer-name*=cta]','[href*=framer.link]','[data-action=login]','[data-action=signup]','.cta-login','.cta-signup'];
    var nodes = document.querySelectorAll(selectors.join(','));
    nodes.forEach(function(btn){
      btn.addEventListener('click', function(e){ e.preventDefault(); openAuth('login'); });
    });
    try { console.log('[auth-connector] initialized; bound', nodes.length, 'elements'); } catch(e){}
  });
})();

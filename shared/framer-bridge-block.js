(function(){
  var selectors = [
    '#framer-badge', '.framer-badge', '.framer-edit-button', '.framer-controls',
    '[data-framer-bridge]', '[data-framer-portal]', '[class*="framer-bridge"]',
    '[class*="framer"] [class*="edit"]',
    'a[href*="framer.com"][aria-label*="Edit"]',
    'a[href*="framer.com"][title*="Edit"]',
    'a[href*="framer.link"]'
  ].join(',');

  function hideFramer(root){
    try{
      (root.querySelectorAll ? root.querySelectorAll(selectors) : []).forEach(function(el){
        el.style.setProperty('visibility','hidden','important');
        el.style.setProperty('pointerEvents','none','important');
        el.style.setProperty('opacity','0','important');
        el.setAttribute('data-framer-removed','1');
      });
    }catch(e){}
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function(){ hideFramer(document); });
  } else {
    hideFramer(document);
  }

  try{
    new MutationObserver(function(mutations){
      mutations.forEach(function(m){
        m.addedNodes && m.addedNodes.forEach(function(n){ if (n.nodeType === 1) hideFramer(n); });
      });
    }).observe(document.documentElement, { childList: true, subtree: true });
  }catch(e){}

  try{
    document.querySelectorAll('script[src*="framer.com"], script[src*="framerusercontent.com"][data-framer], iframe[src*="framer.com"]').forEach(function(node){
      node.parentNode && node.parentNode.removeChild(node);
    });
  }catch(e){}
})();

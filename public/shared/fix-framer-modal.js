// Fix auto-opening modal issues from Framer links
(function() {
  function init() {
    if (window.__anwaltsFramerFixInitialized) return;
    window.__anwaltsFramerFixInitialized = true;

    console.log('🔧 Initializing Framer modal fix...');

    // Clear any problematic localStorage flags and free-limit markers
    try {
      if (localStorage.getItem('open_auth_modal')) {
        console.log('🗑️ Clearing problematic localStorage flag');
        localStorage.removeItem('open_auth_modal');
      }
      localStorage.removeItem('tryout_sent');
      localStorage.removeItem('tryout_conversation');
      localStorage.removeItem('restore_tryout');
    } catch(_) {}

    const selector = 'a[href*="framer.link"], a[href*="framerusercontent.com"], a[href*="framer.com"]';

    function triggerAuthFlow(){
      try {
        if (typeof window.openAuthModal === 'function') {
          window.openAuthModal();
          return true;
        }
        if (typeof window.showSignInModal === 'function') {
          window.showSignInModal();
          return true;
        }
        if (typeof window.__ensureLandingAuthModal === 'function') {
          const overlay = window.__ensureLandingAuthModal();
          if (overlay && typeof overlay.__open === 'function') {
            overlay.__open();
            return true;
          }
        }
      } catch (err) {
        console.warn('⚠️ Failed to trigger auth modal', err);
      }
      return false;
    }

    function bindInterceptors(root) {
      const target = root && root.querySelectorAll ? root : document;
      target.querySelectorAll(selector).forEach(link => {
        if (link.dataset.anwaltsFramerPatched === '1') return;
        link.dataset.anwaltsFramerPatched = '1';
        console.log('🔗 Fixing problematic Framer link:', link.href);
        link.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          console.log('🚫 Blocked Framer external redirect');

          // Instead of redirecting to Framer, trigger local auth modal
          if (!triggerAuthFlow()) {
            console.log('⚠️ No auth modal function available');
          }
          return false;
        }, true);
      });
    }

    // Fix links immediately
    bindInterceptors(document);

    // Fix links that might be added dynamically
    try {
      const observerRoot = document.body || document.documentElement;
      if (observerRoot) {
        new MutationObserver(function(mutations) {
          mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
              bindInterceptors(mutation.target);
            }
          });
        }).observe(observerRoot, {
          childList: true,
          subtree: true
        });
      }
    } catch (err) {
      console.warn('⚠️ Failed to observe DOM for Framer links', err);
    }

    console.log('✅ Framer modal fix initialized');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

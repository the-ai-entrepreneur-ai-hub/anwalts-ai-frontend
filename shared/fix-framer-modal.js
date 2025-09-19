// Fix auto-opening modal issues from Framer links
(function() {
  console.log('🔧 Initializing Framer modal fix...');
  
  // Clear any problematic localStorage flags
  if (localStorage.getItem('open_auth_modal')) {
    console.log('🗑️ Clearing problematic localStorage flag');
    localStorage.removeItem('open_auth_modal');
  }
  
  // Intercept and fix problematic Framer links
  function fixFramerLinks() {
    const problematicLinks = document.querySelectorAll('a[href*="framer.link"]');
    problematicLinks.forEach(link => {
      console.log('🔗 Fixing problematic Framer link:', link.href);
      link.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('🚫 Blocked Framer external redirect');
        
        // Instead of redirecting to Framer, trigger local auth modal
        if (typeof window.openAuthModal === 'function') {
          window.openAuthModal();
        } else if (typeof window.showSignInModal === 'function') {
          window.showSignInModal();
        } else {
          console.log('⚠️ No auth modal function available');
        }
        return false;
      });
    });
  }
  
  // Fix links immediately
  fixFramerLinks();
  
  // Fix links that might be added dynamically
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.type === 'childList') {
        fixFramerLinks();
      }
    });
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
  
  console.log('✅ Framer modal fix initialized');
})();
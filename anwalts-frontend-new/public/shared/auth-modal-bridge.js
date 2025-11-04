/**
 * Auth Modal Bridge
 * Handles opening the auth modal and communicating with parent window
 */
(function() {
  'use strict';

  // Global function to open auth modal
  window.openAuthModal = function(mode) {
    mode = mode || 'login';
    
    // If we're in an iframe, notify parent window
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({
        type: 'ANWALTS_OPEN_AUTH',
        mode: mode
      }, '*');
      // IMPORTANT: Return immediately to prevent iframe fallback
      return;
    }
    
    // If we're the parent window, trigger modal directly
    if (typeof window.__anwaltsAuthModal !== 'undefined') {
      window.__anwaltsAuthModal.open(mode);
    } else {
      console.warn('[Auth Bridge] Modal handler not found on parent');
    }
  };

  // Global function to close auth modal
  window.closeAuthModal = function() {
    // If we're in an iframe, notify parent window
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({
        type: 'ANWALTS_CLOSE_AUTH'
      }, '*');
      return;
    }
    
    // If we're the parent window, close modal directly
    if (typeof window.__anwaltsAuthModal !== 'undefined') {
      window.__anwaltsAuthModal.close();
    }
  };

  // Listen for messages from child frames
  if (typeof window !== 'undefined') {
    window.addEventListener('message', function(event) {
      if (!event.data || !event.data.type) return;
      
      switch (event.data.type) {
        case 'ANWALTS_OPEN_AUTH':
          if (typeof window.openAuthModal === 'function') {
            window.openAuthModal(event.data.mode || 'login');
          }
          break;
        case 'ANWALTS_CLOSE_AUTH':
          if (typeof window.closeAuthModal === 'function') {
            window.closeAuthModal();
          }
          break;
        case 'openSignInModal':
          // Legacy support for old event name
          if (typeof window.openAuthModal === 'function') {
            window.openAuthModal('login');
          }
          break;
      }
    });
  }

  console.log('[Auth Bridge] Initialized');
})();
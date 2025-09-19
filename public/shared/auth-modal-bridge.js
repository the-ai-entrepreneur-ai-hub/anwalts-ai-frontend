// Global bridge to connect Framer iframe with parent auth modal
(function() {
    'use strict';
    
    // Create global function that Framer can call
    window.openAuthModal = function(mode) {
        console.log('🔓 Opening auth modal via global function');
        // Send message to parent window
        if (window.parent && window.parent !== window) {
            window.parent.postMessage({
                type: 'openAuthModal',
                mode: mode || 'signin'
            }, '*');
        }
        // Also trigger on current window if we have the function
        if (window.triggerAuthModal) {
            window.triggerAuthModal(mode);
        }
    };
    
    // Also expose common variations
    window.showSignInModal = function() {
        window.openAuthModal('signin');
    };
    
    window.showSignUpModal = function() {
        window.openAuthModal('signup');
    };
    
    // Listen for messages from parent
    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'authModalReady') {
            console.log('✅ Auth modal bridge connected');
        }
    });
    
    // Notify parent that bridge is ready
    if (window.parent && window.parent !== window) {
        window.parent.postMessage({
            type: 'iframeBridgeReady'
        }, '*');
    }
})();

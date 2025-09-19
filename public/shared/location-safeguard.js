// Early location method safeguard - prevents iframe location.assign errors
(function() {
    'use strict';
    
    // Store original location methods
    const originalAssign = window.location.assign;
    const originalReplace = window.location.replace;
    
    // Override location.assign to be more defensive
    try {
        Object.defineProperty(window.location, 'assign', {
            value: function(url) {
                try {
                    // Check if we're in an iframe
                    if (window !== window.top) {
                        // Post message to parent instead of direct navigation
                        window.parent.postMessage({
                            type: 'navigate',
                            url: url
                        }, '*');
                        return;
                    }
                    // Not in iframe, proceed normally
                    return originalAssign.call(this, url);
                } catch (e) {
                    console.warn('Location assign intercepted:', e);
                    // Fallback to href
                    window.location.href = url;
                }
            },
            configurable: true
        });
        
        Object.defineProperty(window.location, 'replace', {
            value: function(url) {
                try {
                    if (window !== window.top) {
                        window.parent.postMessage({
                            type: 'navigate',
                            url: url
                        }, '*');
                        return;
                    }
                    return originalReplace.call(this, url);
                } catch (e) {
                    console.warn('Location replace intercepted:', e);
                    window.location.href = url;
                }
            },
            configurable: true
        });
    } catch (e) {
        // Silently fail if we can't override (some browsers prevent this)
    }
})();

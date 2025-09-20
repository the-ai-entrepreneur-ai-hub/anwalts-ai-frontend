(function () {
  if (typeof window === 'undefined') return;
  if (window.__anwaltsGButtonLoaded) return;
  window.__anwaltsGButtonLoaded = true;

  const markGoogleButtons = () => {
    const buttons = document.querySelectorAll('[data-provider="google"], [data-auth-provider="google"]');
    if (!buttons || buttons.length === 0) return;
    buttons.forEach((btn) => {
      try {
        btn.dataset.googleBridgeReady = '1';
      } catch (_) {
        /* ignore dataset errors */
      }
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', markGoogleButtons, { once: true });
  } else {
    markGoogleButtons();
  }
})();

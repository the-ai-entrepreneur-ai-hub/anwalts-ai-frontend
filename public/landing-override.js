(function () {
  function closestClickable(el) {
    while (el && el !== document && !(el.tagName === 'A' || el.tagName === 'BUTTON')) el = el.parentElement;
    return el;
  }

  function wantsAuth(el) {
    try {
      const text = (el.textContent || '').toLowerCase();
      const href = (el.getAttribute && el.getAttribute('href')) || '';
      const role = (el.getAttribute && el.getAttribute('role')) || '';
      const dataAuth = (el.getAttribute && el.getAttribute('data-auth')) || '';
      if (dataAuth === 'login' || dataAuth === 'register') return true;
      if (/framer\.(link|com|website|cloud)/i.test(href)) return true;
      if (/^login$|^log in$|anmelden|sign\s*in|einloggen/.test(text)) return true;
      if (/^register$|registrieren|sign\s*up|jetzt\s*starten|start\s*now/.test(text)) return true;
      if (role === 'link' && /auth|login|register/i.test(text)) return true;
      return false;
    } catch (_) {
      return false;
    }
  }

  function redirectToLogin() {
    try {
      const url = new URL('/login', window.location.origin);
      url.searchParams.set('redirect', '/dashboard');
      window.location.assign(url.pathname + url.search);
    } catch (_) {
      window.location.assign('/login?redirect=%2Fdashboard');
    }
  }

  document.addEventListener(
    'click',
    function (event) {
      try {
        const path = event.composedPath && event.composedPath();
        let el = (path && path.length ? path[0] : event.target);
        el = closestClickable(el);
        if (!el) return;
        if (wantsAuth(el)) {
          event.preventDefault();
          event.stopPropagation();
          redirectToLogin();
        }
      } catch (_) {
        // no-op
      }
    },
    true,
  );

  (function patch() {
    function attachHandlers() {
      document
        .querySelectorAll('a[href*="framer."]')
        .forEach(function (anchor) {
          anchor.addEventListener(
            'click',
            function (event) {
              event.preventDefault();
              event.stopPropagation();
              redirectToLogin();
            },
            { capture: true },
          );
        });
    }

    try {
      attachHandlers();
    } catch (_) {
      // no-op
    }

    try {
      new MutationObserver(attachHandlers).observe(document.documentElement, {
        subtree: true,
        childList: true,
      });
    } catch (_) {
      // no-op
    }
  })();
})();

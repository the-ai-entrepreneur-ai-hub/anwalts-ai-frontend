// Disable Framer auth modals by redirecting to the Nuxt login route
(function () {
  function redirectToLogin() {
    try {
      const url = new URL('/login', window.location.origin);
      url.searchParams.set('redirect', '/dashboard');
      window.location.href = url.pathname + url.search;
    } catch (_) {
      window.location.href = '/login?redirect=%2Fdashboard';
    }
  }

  function neutralizeLinks() {
    const selectors = ['a[href*="framer.link"]', 'a[href*="framer.com"]'];
    document.querySelectorAll(selectors.join(',')).forEach((link) => {
      link.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        redirectToLogin();
      });
    });
  }

  neutralizeLinks();

  const observer = new MutationObserver(neutralizeLinks);
  observer.observe(document.body, { childList: true, subtree: true });
})();

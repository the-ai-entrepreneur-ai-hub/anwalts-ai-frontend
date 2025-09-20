// Simple bridge that forwards auth requests to the dedicated login route
(function () {
  'use strict';

  function buildLoginUrl(target) {
    try {
      const redirect = typeof target === 'string' && target.startsWith('/') ? target : '/dashboard';
      const url = new URL('/login', window.location.origin);
      url.searchParams.set('redirect', redirect);
      return url.pathname + url.search;
    } catch (_) {
      return '/login?redirect=%2Fdashboard';
    }
  }

  function goToLogin(target) {
    const destination = buildLoginUrl(target);
    window.location.href = destination;
  }

  window.openAuthModal = function (target) {
    goToLogin(target);
  };

  window.showSignInModal = function (target) {
    goToLogin(target);
  };

  window.showSignUpModal = function (target) {
    goToLogin(target);
  };
})();

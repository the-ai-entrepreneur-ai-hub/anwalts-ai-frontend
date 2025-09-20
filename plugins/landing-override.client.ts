export default defineNuxtPlugin(() => {
  if (process.server) return;

  const inAuth = (el: any) => {
    try {
      return !!(el && el.closest && el.closest('#authModal, #authModalContent, .auth-modal, .auth-modal-overlay, #authForm'));
    } catch {
      return false;
    }
  };

  const isFramer = (url?: string) => !!(url && /framer\.(com|link|website|cloud)/i.test(url));

  const redirectToLogin = () => {
    try {
      const url = new URL('/login', window.location.origin);
      url.searchParams.set('redirect', '/dashboard');
      window.location.assign(url.pathname + url.search);
    } catch {
      window.location.assign('/login?redirect=%2Fdashboard');
    }
  };

  document.addEventListener(
    'click',
    (event: any) => {
      try {
        const path = event.composedPath && event.composedPath();
        let el: any = path && path.length ? path[0] : event.target;
        if (inAuth(el)) return;
        while (el && el !== document && !(el.tagName === 'A' || el.tagName === 'BUTTON')) el = el.parentElement;
        if (!el) return;
        const href = (el.getAttribute && el.getAttribute('href')) || '';
        const text = (el.textContent || '').toLowerCase();
        const dataAuth = (el.getAttribute && el.getAttribute('data-auth')) || '';
        const isLogin = /\b(registrieren|anmelden|sign\s*in|sign\s*up|jetzt\s*starten)\b/.test(text);
        if (isFramer(href) || ((dataAuth === 'login' || dataAuth === 'register' || isLogin) && !inAuth(el))) {
          event.preventDefault();
          event.stopPropagation();
          redirectToLogin();
        }
      } catch {
        // no-op
      }
    },
    true,
  );
});

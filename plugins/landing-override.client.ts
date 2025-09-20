export default defineNuxtPlugin(() => {
  if (process.server) return;
  const inAuth = (el: any) => { try { return !!(el && el.closest && el.closest('#authModal, #authModalContent, .auth-modal, .auth-modal-overlay, #authForm')); } catch { return false; } };
  const isFramer = (url?: string) => !!(url && /framer\.(com|link|website|cloud)/i.test(url));
  document.addEventListener('click', (e: any) => {
    try {
      const path = e.composedPath && e.composedPath();
      let el: any = (path && path.length ? path[0] : e.target);
      if (inAuth(el)) return;
      let a: any = el;
      while (a && a !== document && !(a.tagName === 'A' || a.tagName === 'BUTTON')) a = a.parentElement;
      if (!a) return;
      const href = (a.getAttribute && a.getAttribute('href')) || '';
      const txt = (a.textContent || '').toLowerCase();
      const da = (a.getAttribute && a.getAttribute('data-auth')) || '';
      const isLogin = /\b(registrieren|anmelden|sign\s*in|sign\s*up|jetzt\s*starten)\b/.test(txt);
      if (isFramer(href) || ((da === 'login' || da === 'register' || isLogin) && !inAuth(a))) {
        e.preventDefault(); e.stopPropagation();
        if (typeof (window as any).openAuthModal === 'function') (window as any).openAuthModal();
        else if (typeof (window as any).showSignInModal === 'function') (window as any).showSignInModal();
        else window.location.assign('/assistant');
      }
    } catch {}
  }, true);
});

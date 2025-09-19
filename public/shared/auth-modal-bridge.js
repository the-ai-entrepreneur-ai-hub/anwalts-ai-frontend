
(function () {
  'use strict';

  const CTA_SELECTORS = [
    '[data-auth="cta"]',
    'a[data-auth="login"]',
    'a[data-auth="signup"]',
    'button[data-auth="login"]',
    'button[data-auth="signup"]',
    'a[data-framer-name*="cta" i]',
    'button[data-framer-name*="cta" i]'
  ];

  const CTA_TEXT_MATCHERS = [
    'registrieren',
    'jetzt starten',
    'sign up',
    'signup',
    'login',
    'anmelden',
    'zum dashboard',
    'kostenlos testen'
  ];

  const FOCUSABLE = 'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';
  const GOOGLE_REDIRECT = '/auth/google/authorize?redirect=/dashboard';

  const state = {
    overlay: null,
    modal: null,
    form: null,
    submitButton: null,
    toggleLogin: null,
    toggleSignup: null,
    footerPrompt: null,
    footerToggle: null,
    titleEl: null,
    subtitleEl: null,
    errorEl: null,
    messageEl: null,
    googleBtn: null,
    nameInput: null,
    emailInput: null,
    passwordInput: null,
    confirmInput: null,
    termsCheckbox: null,
    mode: 'login',
    isOpen: false,
    isSubmitting: false,
    lastActive: null,
    focusHandler: null,
    bindTimer: null,
    observer: null
  };

  function ready(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn, { once: true });
    } else {
      fn();
    }
  }

  ready(init);

  function init() {
    bindCtas(document);
    state.observer = new MutationObserver(scheduleBind);
    state.observer.observe(document.documentElement, { childList: true, subtree: true });
    exposeGlobals();
  }

  function scheduleBind() {
    if (state.bindTimer) clearTimeout(state.bindTimer);
    state.bindTimer = setTimeout(() => {
      bindCtas(document);
    }, 80);
  }

  function bindCtas(root) {
    const candidates = new Set();
    CTA_SELECTORS.forEach((selector) => {
      root.querySelectorAll(selector).forEach((node) => {
        candidates.add(node);
      });
    });

    root.querySelectorAll('a, button').forEach((node) => {
      if (!node || node.dataset.authBound === '1') return;
      const text = (node.textContent || '').trim().toLowerCase();
      if (!text) return;
      if (CTA_TEXT_MATCHERS.some((match) => text.includes(match))) {
        candidates.add(node);
      }
    });

    candidates.forEach((node) => {
      if (node.dataset.authBound === '1') return;
      node.dataset.authBound = '1';
      setPointerDefaults(node);
      node.addEventListener('click', (event) => {
        try {
          event.preventDefault();
          event.stopPropagation();
        } catch (_) {}
        openAuthModal(deriveMode(node));
      });
    });
  }

  function setPointerDefaults(node) {
    try {
      if (getComputedStyle(node).pointerEvents === 'none') {
        node.style.pointerEvents = 'auto';
      }
    } catch (_) {}
  }

  function deriveMode(node) {
    if (!node) return 'login';
    const attr = (node.getAttribute('data-auth-mode') || '').toLowerCase();
    if (attr === 'signup' || attr === 'register') return 'signup';
    if (attr === 'login' || attr === 'signin') return 'login';
    const text = (node.textContent || '').toLowerCase();
    if (text.includes('registr') || text.includes('sign up')) return 'signup';
    return 'login';
  }

  function exposeGlobals() {
    window.openAuthModal = openAuthModal;
    window.closeAuthModal = closeAuthModal;

    window.addEventListener('message', (event) => {
      if (!event || typeof event.data !== 'object') return;
      if (event.data.type === 'ANWALTS_OPEN_AUTH') openAuthModal(event.data.mode);
      if (event.data.type === 'ANWALTS_CLOSE_AUTH') closeAuthModal();
    });

    window.dispatchEvent(new CustomEvent('anwalts-auth-bridge-ready'));
  }

  function openAuthModal(mode) {
    const normalized = normalizeMode(mode);
    if (typeof window.__anwaltsAuthOpen === 'function') {
      window.__anwaltsAuthOpen(normalized);
      return;
    }
    if (window.parent && window.parent !== window) {
      try {
        window.parent.postMessage({ type: 'ANWALTS_OPEN_AUTH', mode: normalized }, '*');
      } catch (_) {}
    }
    useFallbackOpen(normalized);
  }

  function closeAuthModal() {
    if (typeof window.__anwaltsAuthClose === 'function') {
      window.__anwaltsAuthClose();
      return;
    }
    useFallbackClose();
  }

  function normalizeMode(value) {
    const lowered = (value || '').toLowerCase();
    return lowered === 'signup' || lowered === 'register' || lowered === 'sign-up' ? 'signup' : 'login';
  }

  function useFallbackOpen(mode) {
    ensureModal();
    state.mode = mode;
    updateModeUI();
    if (state.isOpen) return;
    state.isOpen = true;
    state.lastActive = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    document.body.classList.add('anwalts-auth-modal-open');
    state.overlay.classList.add('is-open');
    state.overlay.setAttribute('aria-hidden', 'false');
    activateFocusTrap();
    requestAnimationFrame(() => {
      focusInitialField();
    });
  }

  function useFallbackClose() {
    if (!state.overlay || !state.isOpen) return;
    state.isOpen = false;
    document.body.classList.remove('anwalts-auth-modal-open');
    state.overlay.classList.remove('is-open');
    state.overlay.setAttribute('aria-hidden', 'true');
    deactivateFocusTrap();
    clearError();
    clearMessage();
    if (state.lastActive && typeof state.lastActive.focus === 'function') {
      try { state.lastActive.focus(); } catch (_) {}
    }
    state.lastActive = null;
  }

  function ensureModal() {
    if (state.overlay) return;
    const overlay = document.createElement('div');
    overlay.className = 'anwalts-auth-overlay';
    overlay.setAttribute('data-mode', state.mode);
    overlay.setAttribute('aria-hidden', 'true');
    overlay.innerHTML = [
      '<div class="anwalts-auth-modal" data-auth-dialog role="dialog" aria-modal="true" aria-labelledby="anwalts-auth-title" tabindex="-1">',
      '  <button type="button" class="anwalts-auth-close" data-auth-close aria-label="Schließen"><span aria-hidden="true">&times;</span></button>',
      '  <div class="anwalts-auth-header">',
      '    <h2 class="anwalts-auth-title" id="anwalts-auth-title">Willkommen zurück</h2>',
      '    <p class="anwalts-auth-subtitle" data-auth-subtitle>Melden Sie sich an, um Ihr Kanzlei-Dashboard zu öffnen.</p>',
      '  </div>',
      '  <div class="anwalts-auth-toggle">',
      '    <button type="button" data-auth-toggle="login" class="is-active">Anmelden</button>',
      '    <button type="button" data-auth-toggle="signup">Registrieren</button>',
      '  </div>',
      '  <button type="button" class="anwalts-auth-google" data-auth-google>',
      '    <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#4285f4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34a853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#fbbc05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#ea4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>',
      '    <span>Mit Google fortfahren</span>',
      '  </button>',
      '  <div class="anwalts-auth-divider"><span>oder mit E-Mail</span></div>',
      '  <form class="anwalts-auth-form" data-auth-form novalidate>',
      '    <div class="anwalts-auth-field" data-auth-section="signup">',
      '      <label for="anwalts-auth-name">Vollständiger Name</label>',
      '      <input id="anwalts-auth-name" name="name" type="text" autocomplete="name" placeholder="Dr. Max Müller">',
      '    </div>',
      '    <div class="anwalts-auth-field">',
      '      <label for="anwalts-auth-email">E-Mail-Adresse</label>',
      '      <input id="anwalts-auth-email" name="email" type="email" autocomplete="email" placeholder="kanzlei@example.de" required>',
      '    </div>',
      '    <div class="anwalts-auth-field">',
      '      <label for="anwalts-auth-password">Passwort</label>',
      '      <input id="anwalts-auth-password" name="password" type="password" autocomplete="current-password" placeholder="••••••••" required>',
      '    </div>',
      '    <div class="anwalts-auth-field" data-auth-section="signup">',
      '      <label for="anwalts-auth-confirm">Passwort bestätigen</label>',
      '      <input id="anwalts-auth-confirm" name="confirm" type="password" autocomplete="new-password" placeholder="Passwort bestätigen">',
      '    </div>',
      '    <label class="anwalts-auth-checkbox" data-auth-section="signup">',
      '      <input type="checkbox" name="terms">',
      '      <span>Ich stimme den <a href="/terms" target="_blank" rel="noopener">AGB</a> und <a href="/privacy" target="_blank" rel="noopener">Datenschutzbestimmungen</a> zu.</span>',
      '    </label>',
      '    <div class="anwalts-auth-error" data-auth-error role="alert" aria-live="polite"></div>',
      '    <div class="anwalts-auth-message" data-auth-message aria-live="polite"></div>',
      '    <button type="submit" class="anwalts-auth-submit" data-auth-submit>Anmelden</button>',
      '  </form>',
      '  <div class="anwalts-auth-footer">',
      '    <span data-auth-footer-prompt>Neu bei ANWALTS.AI?</span>',
      '    <button type="button" data-auth-footer-toggle>Jetzt registrieren</button>',
      '  </div>',
      '</div>'
    ].join('');

    document.body.appendChild(overlay);
    state.overlay = overlay;
    state.modal = overlay.querySelector('[data-auth-dialog]');
    state.form = overlay.querySelector('[data-auth-form]');
    state.submitButton = overlay.querySelector('[data-auth-submit]');
    state.toggleLogin = overlay.querySelector('[data-auth-toggle="login"]');
    state.toggleSignup = overlay.querySelector('[data-auth-toggle="signup"]');
    state.footerPrompt = overlay.querySelector('[data-auth-footer-prompt]');
    state.footerToggle = overlay.querySelector('[data-auth-footer-toggle]');
    state.titleEl = overlay.querySelector('#anwalts-auth-title');
    state.subtitleEl = overlay.querySelector('[data-auth-subtitle]');
    state.errorEl = overlay.querySelector('[data-auth-error]');
    state.messageEl = overlay.querySelector('[data-auth-message]');
    state.googleBtn = overlay.querySelector('[data-auth-google]');
    state.nameInput = overlay.querySelector('#anwalts-auth-name');
    state.emailInput = overlay.querySelector('#anwalts-auth-email');
    state.passwordInput = overlay.querySelector('#anwalts-auth-password');
    state.confirmInput = overlay.querySelector('#anwalts-auth-confirm');
    state.termsCheckbox = overlay.querySelector('input[name="terms"]');

    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) closeAuthModal();
    });

    const closeBtn = overlay.querySelector('[data-auth-close]');
    if (closeBtn) closeBtn.addEventListener('click', closeAuthModal);

    if (state.toggleLogin) state.toggleLogin.addEventListener('click', () => setMode('login'));
    if (state.toggleSignup) state.toggleSignup.addEventListener('click', () => setMode('signup'));
    if (state.footerToggle) state.footerToggle.addEventListener('click', () => setMode(state.mode === 'login' ? 'signup' : 'login'));

    if (state.googleBtn) {
      state.googleBtn.addEventListener('click', (event) => {
        event.preventDefault();
        window.location.href = GOOGLE_REDIRECT;
      });
    }

    if (state.form) state.form.addEventListener('submit', handleSubmit);
  }

  function setMode(mode) {
    if (state.mode === mode) return;
    state.mode = mode;
    updateModeUI();
    clearError();
    clearMessage();
    if (state.isOpen) setTimeout(() => focusInitialField(), 40);
  }

  function updateModeUI() {
    if (!state.overlay) return;
    state.overlay.setAttribute('data-mode', state.mode);
    if (state.toggleLogin && state.toggleSignup) {
      if (state.mode === 'login') {
        state.toggleLogin.classList.add('is-active');
        state.toggleSignup.classList.remove('is-active');
      } else {
        state.toggleSignup.classList.add('is-active');
        state.toggleLogin.classList.remove('is-active');
      }
    }
    if (state.titleEl) state.titleEl.textContent = state.mode === 'signup' ? 'Konto erstellen' : 'Willkommen zurück';
    if (state.subtitleEl) {
      state.subtitleEl.textContent = state.mode === 'signup'
        ? 'Registrieren Sie sich kostenlos und starten Sie mit ANWALTS.AI.'
        : 'Melden Sie sich an, um Ihr Kanzlei-Dashboard zu öffnen.';
    }
    if (state.submitButton) {
      state.submitButton.textContent = state.mode === 'signup' ? 'Registrieren' : 'Anmelden';
    }
    if (state.footerPrompt && state.footerToggle) {
      if (state.mode === 'signup') {
        state.footerPrompt.textContent = 'Bereits Kunde?';
        state.footerToggle.textContent = 'Jetzt anmelden';
      } else {
        state.footerPrompt.textContent = 'Neu bei ANWALTS.AI?';
        state.footerToggle.textContent = 'Jetzt registrieren';
      }
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    if (state.isSubmitting) return;
    clearError();
    clearMessage();

    const email = (state.emailInput && state.emailInput.value || '').trim().toLowerCase();
    const password = (state.passwordInput && state.passwordInput.value) || '';

    if (!/.+@.+\..+/.test(email)) {
      setError('Bitte geben Sie eine gültige E-Mail-Adresse ein.');
      if (state.emailInput) state.emailInput.focus();
      return;
    }

    if (!password || password.length < 6) {
      setError('Bitte geben Sie ein Passwort mit mindestens 6 Zeichen ein.');
      if (state.passwordInput) state.passwordInput.focus();
      return;
    }

    if (state.mode === 'signup') {
      const name = (state.nameInput && state.nameInput.value || '').trim();
      const confirm = (state.confirmInput && state.confirmInput.value) || '';
      const termsAccepted = state.termsCheckbox ? state.termsCheckbox.checked : false;

      if (!name) {
        setError('Bitte geben Sie Ihren Namen an.');
        if (state.nameInput) state.nameInput.focus();
        return;
      }
      if (!confirm || confirm !== password) {
        setError('Bitte bestätigen Sie Ihr Passwort.');
        if (state.confirmInput) state.confirmInput.focus();
        return;
      }
      if (!termsAccepted) {
        setError('Bitte akzeptieren Sie die Bedingungen.');
        if (state.termsCheckbox) state.termsCheckbox.focus();
        return;
      }
      setSubmitting(true);
      performSignup({ email, password, name })
        .catch((error) => setError(error && error.message ? error.message : 'Registrierung fehlgeschlagen.'))
        .finally(() => setSubmitting(false));
      return;
    }

    setSubmitting(true);
    performLogin({ email, password })
      .catch((error) => setError(error && error.message ? error.message : 'Anmeldung fehlgeschlagen.'))
      .finally(() => setSubmitting(false));
  }

  function setSubmitting(flag) {
    state.isSubmitting = flag;
    if (!state.submitButton) return;
    state.submitButton.disabled = !!flag;
    state.submitButton.textContent = flag
      ? (state.mode === 'signup' ? 'Registrieren…' : 'Anmelden…')
      : (state.mode === 'signup' ? 'Registrieren' : 'Anmelden');
  }

  function performLogin(payload) {
    return fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload)
    })
      .then(parseJsonResponse)
      .then((data) => {
        if (!data) throw new Error('Server nicht erreichbar.');
        if (data.error || data.success === false) {
          throw new Error(data.error || data.message || 'Anmeldung fehlgeschlagen.');
        }
        const token = data.token || data.access_token;
        if (!token) throw new Error('Token konnte nicht erstellt werden.');
        persistSession(token, data.user || { email: payload.email });
        setMessage('Weiterleitung zum Dashboard …');
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 350);
      })
      .catch((error) => {
        throw error instanceof Error ? error : new Error(String(error || 'Fehler'));
      });
  }

  function performSignup(payload) {
    return fetch('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email: payload.email, name: payload.name, password: payload.password })
    })
      .then(parseJsonResponse)
      .then((data) => {
        if (data && data.detail) {
          throw new Error(typeof data.detail === 'string' ? data.detail : 'Registrierung fehlgeschlagen.');
        }
        if (data && data.error) {
          throw new Error(data.error);
        }
        return performLogin({ email: payload.email, password: payload.password });
      })
      .catch((error) => {
        throw error instanceof Error ? error : new Error(String(error || 'Registrierung fehlgeschlagen.'));
      });
  }

  function parseJsonResponse(response) {
    if (!response) return Promise.reject(new Error('Keine Antwort.'));
    return response.text().then((text) => {
      if (!text) return {};
      try {
        return JSON.parse(text);
      } catch (_) {
        return {};
      }
    });
  }

  function persistSession(token, user) {
    try {
      localStorage.setItem('anwalts_auth_token', token);
      if (user) localStorage.setItem('anwalts_user', JSON.stringify(user));
    } catch (_) {}

    const maxAge = 60 * 60 * 24;
    const base = 'sat=' + encodeURIComponent(token) + '; path=/; max-age=' + maxAge + '; secure; samesite=None';
    document.cookie = base;
    try {
      const hostParts = window.location.hostname.split('.');
      if (hostParts.length > 2) {
        document.cookie = base + '; domain=.' + hostParts.slice(-2).join('.');
      }
    } catch (_) {}
  }

  function focusInitialField() {
    const target = state.mode === 'signup' ? state.nameInput : state.emailInput;
    if (target && typeof target.focus === 'function') {
      target.focus();
      return;
    }
    try { if (state.modal) state.modal.focus(); } catch (_) {}
  }

  function activateFocusTrap() {
    if (state.focusHandler) return;
    state.focusHandler = (event) => {
      if (!state.isOpen || !state.modal) return;
      if (event.key === 'Escape') {
        event.preventDefault();
        closeAuthModal();
        return;
      }
      if (event.key !== 'Tab') return;
      const focusable = Array.from(state.modal.querySelectorAll(FOCUSABLE))
        .filter((el) => el && el.offsetParent !== null && !el.hasAttribute('disabled'));
      if (!focusable.length) {
        event.preventDefault();
        return;
      }
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey) {
        if (document.activeElement === first) {
          event.preventDefault();
          last.focus();
        }
      } else if (document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    document.addEventListener('keydown', state.focusHandler, true);
  }

  function deactivateFocusTrap() {
    if (!state.focusHandler) return;
    document.removeEventListener('keydown', state.focusHandler, true);
    state.focusHandler = null;
  }

  function clearError() {
    if (state.errorEl) state.errorEl.textContent = '';
  }

  function setError(message) {
    if (state.errorEl) state.errorEl.textContent = message;
  }

  function clearMessage() {
    if (state.messageEl) state.messageEl.textContent = '';
  }

  function setMessage(message) {
    if (state.messageEl) state.messageEl.textContent = message;
  }
})();

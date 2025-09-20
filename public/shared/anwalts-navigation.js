(function () {
  function redirectToLogin(targetPath) {
    try {
      const redirect = typeof targetPath === 'string' && targetPath.startsWith('/') ? targetPath : '/dashboard';
      const url = new URL('/login', window.location.origin);
      url.searchParams.set('redirect', redirect);
      window.location.href = url.pathname + url.search;
    } catch (_) {
      window.location.href = '/login?redirect=%2Fdashboard';
    }
  }

  function ensureAuthOrLoginRedirect(targetPath) {
    try {
      const hasToken = !!localStorage.getItem('anwalts_auth_token');
      if (!hasToken) {
        redirectToLogin(targetPath);
        return false;
      }
    } catch (_) {
      redirectToLogin(targetPath);
      return false;
    }
    return true;
  }

  window.anwaltsNavigationManager = window.anwaltsNavigationManager || {
    goToDashboard() {
      if (ensureAuthOrLoginRedirect('/dashboard')) window.location.href = '/dashboard';
    },
    goHome() {
      window.location.href = '/';
    },
  };

  function isAssistantEnabled() {
    return true;
  }

  function createAssistantLink() {
    const a = document.createElement('a');
    a.href = '/assistant';
    a.textContent = 'KI-Assistent';
    a.setAttribute('aria-label', 'KI-Assistent');
    a.style.cursor = 'pointer';
    return a;
  }

  function createSidebarAssistantItem() {
    const item = document.createElement('div');
    item.className = 'nav-item flex items-center gap-3 px-4 py-3 rounded-lg cursor-pointer';
    item.setAttribute('data-section', 'assistant');
    item.innerHTML = '<i data-lucide="messages-square" class="w-5 h-5"></i><span>KI-Assistent</span>';
    item.addEventListener('click', function () {
      window.location.href = '/assistant';
    });
    return item;
  }

  function injectAssistantTab() {
    try {
      const sidebarNav = document.querySelector('.nav-sidebar nav');
      if (sidebarNav && !sidebarNav.querySelector('[data-section="assistant"]')) {
        const dashboardItem = sidebarNav.querySelector('[data-section="dashboard"]');
        const assistantItem = createSidebarAssistantItem();
        if (dashboardItem && dashboardItem.parentNode) {
          dashboardItem.parentNode.insertBefore(assistantItem, dashboardItem.nextSibling);
        } else {
          sidebarNav.appendChild(assistantItem);
        }
      }

      const dashboardLinks = Array.from(document.querySelectorAll('a[href="/dashboard"]'));
      if (dashboardLinks.length > 0) {
        const dash = dashboardLinks[0];
        if (!document.querySelector('a[href="/assistant"]')) {
          const a = createAssistantLink();
          dash.parentNode.insertBefore(a, dash.nextSibling);
          if (dash.parentElement && getComputedStyle(dash.parentElement).display.includes('flex')) {
            a.style.marginLeft = '16px';
          }
        }
        return;
      }

      const primaryNav = document.querySelector('nav[aria-label="Primary"]');
      if (primaryNav && !primaryNav.querySelector('a[href="/assistant"]')) {
        primaryNav.appendChild(createAssistantLink());
      }
    } catch (_) {
      // no-op
    }
  }

  function removeAssistantEntries() {
    try {
      document.querySelectorAll('a[href="/assistant"]').forEach((n) => n.remove());
      const side = document.querySelector('[data-section="assistant"]');
      if (side && side.parentNode) side.parentNode.removeChild(side);
      const fab = document.getElementById('assistant-fab');
      if (fab) fab.remove();
    } catch (_) {
      // no-op
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (isAssistantEnabled()) injectAssistantTab();
    else removeAssistantEntries();
  });
})();

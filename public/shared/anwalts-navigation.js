(function(){
  function ensureAuthOrLoginRedirect(targetPath){
    try{
      const hasToken = !!localStorage.getItem('anwalts_auth_token');
      if(!hasToken){
        // Open login modal on homepage; otherwise navigate to homepage with login trigger
        if(window.location.pathname === '/'){
          if (typeof window.openAuthModal === 'function') {
            window.openAuthModal();
          } else {
            // FIXED: Removed auto-modal trigger
            // const url = new URL(window.location.href);
            // url.searchParams.set('login','1');
            // window.location.replace(url.toString());
            console.log('Auth required, but auto-modal disabled');
          }
        } else {
          // FIXED: Removed auto-modal trigger redirect
          // window.location.href='/?login=1';
          console.log('Navigation auth required, but auto-modal disabled');
        }
        return false;
      }
    }catch(e){}
    return true;
  }
  window.anwaltsNavigationManager = window.anwaltsNavigationManager || {
    goToDashboard(){ if(ensureAuthOrLoginRedirect('/dashboard')) window.location.href='/dashboard'; },
    goHome(){ window.location.href='/'; }
  };

  // Feature flag: KI-Assistent (enabled)
  function isAssistantEnabled(){
    return true;
  }

  function createAssistantLink(){
    const a = document.createElement('a');
    a.href = '/assistant';
    a.textContent = 'KI-Assistent';
    a.setAttribute('aria-label','KI-Assistent');
    a.style.cursor = 'pointer';
    return a;
  }

  function createSidebarAssistantItem(){
    const item = document.createElement('div');
    item.className = 'nav-item flex items-center gap-3 px-4 py-3 rounded-lg cursor-pointer';
    item.setAttribute('data-section','assistant');
    item.innerHTML = '<i data-lucide="messages-square" class="w-5 h-5"></i><span>KI-Assistent</span>';
    item.addEventListener('click', function(){ window.location.href='/assistant'; });
    return item;
  }

  function injectAssistantTab(){
    try {
      // Sidebar (Dashboard) navigation injection
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

      // Try to insert after Dashboard link
      const dashboardLinks = Array.from(document.querySelectorAll('a[href="/dashboard"]'));
      if (dashboardLinks.length > 0) {
        const dash = dashboardLinks[0];
        // Avoid duplicate
        if (!document.querySelector('a[href="/assistant"]')) {
          const a = createAssistantLink();
          dash.parentNode.insertBefore(a, dash.nextSibling);
          // Spacing if inline nav
          if (dash.parentElement && getComputedStyle(dash.parentElement).display.includes('flex')) {
            a.style.marginLeft = '16px';
          }
        }
        return;
      }

      // Try primary nav container
      const primaryNav = document.querySelector('nav[aria-label="Primary"]');
      if (primaryNav && !primaryNav.querySelector('a[href="/assistant"]')) {
        primaryNav.appendChild(createAssistantLink());
        return;
      }

      // No floating fallback; only header/sidebar links are allowed
    } catch (e) { /* no-op */ }
  }

  function removeAssistantEntries(){
    try {
      document.querySelectorAll('a[href="/assistant"]').forEach(n => n.remove());
      const side = document.querySelector('[data-section="assistant"]');
      if (side && side.parentNode) side.parentNode.removeChild(side);
      const fab = document.getElementById('assistant-fab');
      if (fab) fab.remove();
    } catch(_){}
  }

  document.addEventListener('DOMContentLoaded', function(){
    if (isAssistantEnabled()) injectAssistantTab(); else removeAssistantEntries();
  });
})();

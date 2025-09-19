import { defineNuxtPlugin, useRouter } from '#app';

export default defineNuxtPlugin(() => {
  if (process.server) return;
  const router = useRouter();
  const on = (el: Element | null, type: string, fn: (e: Event)=>void, opts?: AddEventListenerOptions) => {
    if (el) el.addEventListener(type, fn as any, opts ?? { passive: true });
  };
  const byId = (id: string) => document.getElementById(id);
  const qs = (sel: string, root: ParentNode = document) => root.querySelector(sel) as HTMLElement | null;
  const qsa = (sel: string, root: ParentNode = document) => Array.from(root.querySelectorAll(sel)) as HTMLElement[];

  // Create tour overlay once
  const ensureTour = () => {
    if (byId('tourOverlay')) return;
    const overlay = document.createElement('div');
    overlay.id = 'tourOverlay';
    Object.assign(overlay.style, { position: 'fixed', inset: '0', background: 'rgba(0,0,0,0.45)', zIndex: '9999', display: 'none' as const });

    const step = document.createElement('div');
    step.id = 'tourStep';
    Object.assign(step.style, { position: 'fixed', top: '72px', right: '24px', maxWidth: '420px', background: '#fff', borderRadius: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.2)', padding: '16px', display: 'none' as const, zIndex: '10000' });

    step.innerHTML = `
      <div style='font-weight:600;margin-bottom:6px'>Kurze Tour</div>
      <div id='tourBody' style='font-size:14px;color:#4b5563;line-height:1.4'>
        Willkommen! Links ist die Navigation. Oben finden Sie Suche und die Glocke. Unten können Sie schnell mit der KI starten.
      </div>
      <div style='margin-top:12px;display:flex;gap:8px;justify-content:flex-end'>
        <button id='tourClose' class='btn-secondary' style='padding:6px 10px;border:1px solid #e5e7eb;border-radius:8px;background:#fff;color:#111827'>Schließen</button>
        <button id='tourNext' class='btn-primary' style='padding:6px 10px;border-radius:8px;background:#2563eb;color:#fff'>Weiter</button>
      </div>`;

    document.body.appendChild(overlay);
    document.body.appendChild(step);

    const hide = () => { overlay.style.display = 'none'; step.style.display = 'none'; };
    on(overlay, 'click', hide);
    on(step.querySelector('#tourClose'), 'click', hide);
    on(step.querySelector('#tourNext'), 'click', () => { hide(); });
  };

  const startTour = () => {
    ensureTour();
    const overlay = byId('tourOverlay')!;
    const step = byId('tourStep')!;
    overlay.style.display = 'block';
    step.style.display = 'block';
  };

  // Add Start Tour button to dashboard header if missing
  const ensureStartButton = () => {
    if (byId('btnStartTour')) return;
    if (!location.pathname.startsWith('/dashboard')) return;
    const hdr = document.querySelector('header .flex.items-center.justify-between') as HTMLElement | null
      || document.querySelector('header') as HTMLElement | null;
    if (!hdr) return;
    const right = document.createElement('div');
    right.style.display = 'flex';
    right.style.gap = '8px';
    right.style.marginLeft = 'auto';
    const btn = document.createElement('button');
    btn.id = 'btnStartTour';
    btn.textContent = 'Tour starten';
    Object.assign(btn.style, { padding: '8px 12px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer' });
    right.appendChild(btn);
    hdr.appendChild(right);
    on(btn, 'click', (e)=>{ e.preventDefault(); startTour(); }, { passive: false });
  };

  const initAccountClick = () => {
    const blocked = document.querySelector('aside .border-t.pointer-events-none');
    if (blocked) blocked.classList.remove('pointer-events-none');
    const account = document.querySelector('aside .border-t');
    if (account) { (account as HTMLElement).style.cursor = 'pointer'; on(account, 'click', () => router.push('/settings'), { passive: true }); }
  };

  const initHelpButtons = () => {
    on(byId('btnStartTour'), 'click', (e)=>{ e.preventDefault(); startTour(); }, { passive: false });
    on(byId('btnHelp'), 'click', (e)=>{ e.preventDefault(); startTour(); }, { passive: false });
  };

  // Global search: Enter triggers navigation to documents with query, and '/' shortcut focuses search
  const initSearch = () => {
    const input = byId('globalSearch') as HTMLInputElement | null;
    if (!input) return;
    on(input, 'keydown', (e: any) => {
      if (e.key === 'Enter') {
        const q = input.value.trim();
        if (q.length > 0) router.push(`/documents?search=${encodeURIComponent(q)}`);
      }
    }, { passive: true });
    window.addEventListener('keydown', (ev: any) => {
      const tag = (ev.target as HTMLElement)?.tagName?.toLowerCase();
      if (tag === 'input' || tag === 'textarea' || (ev as any).isComposing) return;
      if (ev.key === '/' || ev.key === 'f') {
        ev.preventDefault();
        input.focus();
      }
    }, { passive: false } as any);
  };

  // Notifications bell: toggle a simple dropdown panel
  const initNotifications = () => {
    const bell = qs('button[aria-label*=Benachr][aria-label],button[title*=Benachr][title]')
      || qs('button[aria-label*=Nachricht][aria-label],button[title*=Nachricht][title]');
    if (!bell) return;
    let panel = byId('notificationsPanel');
    if (!panel) {
      panel = document.createElement('div');
      panel.id = 'notificationsPanel';
      Object.assign(panel.style, { position: 'absolute', right: '24px', top: '64px', width: '320px', background: '#fff', border: '1px solid #e5e7eb', borderRadius: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.12)', display: 'none', zIndex: '10000' });
      panel.innerHTML = `
        <div style='padding:12px 14px; font-weight:600; border-bottom:1px solid #eee'>Benachrichtigungen</div>
        <div id='notifBody' style='max-height:300px; overflow:auto'>
          <div style='padding:12px 14px; color:#6b7280'>Keine neuen Benachrichtigungen</div>
        </div>`;
      document.body.appendChild(panel);
      window.addEventListener('click', (e) => {
        const t = e.target as Node;
        if (!panel!.contains(t) && t !== bell) (panel as HTMLElement).style.display = 'none';
      }, { passive: true } as any);
    }
    on(bell, 'click', (e) => {
      e.preventDefault();
      const el = panel as HTMLElement;
      el.style.display = el.style.display === 'none' || el.style.display === '' ? 'block' : 'none';
    }, { passive: false });
  };

  // Details toggles: expand/collapse nearest details block or create a placeholder
  const initDetailsToggle = () => {
    document.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      const btn = target.closest('.toggle-details') as HTMLElement | null;
      if (!btn) return;
      e.preventDefault();
      let host = btn.closest('[data-document], .document, .card, li, tr') as HTMLElement | null;
      if (!host) host = btn.parentElement as HTMLElement | null;
      if (!host) return;
      let det = host.querySelector('[data-details], .details') as HTMLElement | null;
      if (!det) {
        det = document.createElement('div');
        det.setAttribute('data-details', '');
        det.style.marginTop = '8px';
        det.style.padding = '8px 10px';
        det.style.background = '#f9fafb';
        det.style.border = '1px solid #e5e7eb';
        det.style.borderRadius = '8px';
        det.textContent = 'Keine weiteren Details verfügbar.';
        host.appendChild(det);
      }
      const expanded = det.style.display !== 'none';
      det.style.display = expanded ? 'none' : 'block';
      btn.setAttribute('aria-expanded', expanded ? 'false' : 'true');
    }, { passive: false } as any);
  };

  // Template creation button: navigate to templates with creation flag
  const initTemplateCreate = () => {
    const btn = qs('button[aria-label*=Neue Vorlage]');
    if (!btn) return;
    on(btn, 'click', (e) => { e.preventDefault(); router.push('/templates?create=1'); }, { passive: false });
  };
    // Fallback floating button if header injection fails
    window.setTimeout(() => {
      if (byId('btnStartTour')) return;
      const fab = document.createElement('button');
      fab.id = 'btnStartTour';
      fab.textContent = 'Tour';
      Object.assign(fab.style, { position: 'fixed', right: '20px', bottom: '20px', padding: '10px 12px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '999px', boxShadow: '0 6px 18px rgba(0,0,0,0.2)', zIndex: '10001', cursor: 'pointer' });
      document.body.appendChild(fab);
      on(fab, 'click', (e)=>{ e.preventDefault(); startTour(); }, { passive: false });
    }, 1200);

  // 'Alle anzeigen' buttons: navigate to the relevant index page
  const initShowAll = () => {
    const candidates = qsa('button, a');
    candidates.forEach(el => {
      const text = (el.textContent || '').trim().toLowerCase();
      if (!text) return;
      if (text.includes('alle anzeigen') || text === 'alle' || text.includes('alle')) {
        let href = '/documents';
        const sectionText = (el.closest('section, div')?.textContent || '').toLowerCase();
        if (sectionText.includes('vorlagen')) href = '/templates';
        else if (sectionText.includes('fälle') || sectionText.includes('akte') || sectionText.includes('cases')) href = '/dashboard/cases';
        on(el, 'click', (e) => { e.preventDefault(); router.push(href); }, { passive: false });
      }
    });
  };

  // Activity loader: hide skeleton and show content after a short delay; best-effort data fill
  const initActivityLoader = async () => {
    const skeleton = byId('activitySkeleton');
    const body = byId('activityBody');
    if (!skeleton && !body) return;
    const finish = () => {
      if (skeleton) skeleton.classList.add('hidden');
      if (body) body.classList.remove('hidden');
    };
    try {
      const res = await fetch('/api/auth/users');
      if (res.ok) {
        const data = await res.json().catch(()=>null) as any;
        const users = (data?.users || []).slice(0, 5);
        if (body && users.length) {
          const ul = document.createElement('ul');
          ul.style.listStyle = 'none'; ul.style.padding = '0'; ul.style.margin = '0';
          users.forEach((u: any) => {
            const li = document.createElement('li');
            li.style.padding = '8px 0';
            li.style.borderBottom = '1px solid #eee';
            li.textContent = `${u.name || u.email} – ${u.role || ''}`;
            ul.appendChild(li);
          });
          (body as HTMLElement).innerHTML = '';
          body!.appendChild(ul);
        }
      }
    } catch {
      // ignore
    }
    window.setTimeout(finish, 500);
  };

  const init = () => {
    ensureTour();
    ensureStartButton();
    initAccountClick();
    initHelpButtons();
    initSearch();
    initNotifications();
    initDetailsToggle();
    initTemplateCreate();
    initShowAll();
    initActivityLoader();

    // Retry start button in case header renders late
    let tries = 0;
    const iv = window.setInterval(() => {
      if (byId('btnStartTour')) { window.clearInterval(iv); return; }
      ensureStartButton();
      tries += 1;
      if (tries >= 10) window.clearInterval(iv);
    }, 500);
  };

  if (document.readyState === 'complete' || document.readyState === 'interactive') setTimeout(init, 0);
  else window.addEventListener('DOMContentLoaded', init as any);
});

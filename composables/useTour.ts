type TourStep = { sel: string; text: string }

type TourConfig = {
  overlayId?: string
  stepId?: string
  contentId?: string
  prevId?: string
  nextId?: string
  closeId?: string
  neverId?: string
  storageKey?: string
}

export function useTour(config: TourConfig = {}) {
  const overlayId = config.overlayId || 'tourOverlay'
  const stepId = config.stepId || 'tourStep'
  const contentId = config.contentId || 'tourContent'
  const prevId = config.prevId || 'tourPrev'
  const nextId = config.nextId || 'tourNext'
  const closeId = config.closeId || 'tourClose'
  const neverId = config.neverId || 'tourNever'
  const storageKey = config.storageKey || 'tourDismissed'

  const state = { idx: 0, steps: [] as TourStep[] }

  const $id = (id: string) => document.getElementById(id) as HTMLElement | null
  const $ = (sel: string) => document.querySelector(sel) as HTMLElement | null

  function setSteps(steps: TourStep[]) {
    state.steps = Array.isArray(steps) ? steps.slice() : []
  }

  function isDismissed(): boolean {
    try { return localStorage.getItem(storageKey) === '1' } catch { return false }
  }

  function dismiss() {
    try { localStorage.setItem(storageKey, '1') } catch {}
  }

  function placeStep() {
    const overlay = $id(overlayId)
    const box = $id(stepId)
    const content = $id(contentId)
    const step = state.steps[state.idx]
    const el = step ? $(step.sel) : null

    // If core elements are missing, do nothing (avoid endTour hiding UI silently)
    if (!overlay || !box || !content) return

    // Ensure overlay and step are attached to body to avoid positioned ancestors
    try {
      if (overlay.parentElement !== document.body) document.body.appendChild(overlay)
      if (box.parentElement !== document.body) document.body.appendChild(box)
    } catch {}

    // Show overlay and step box
    overlay.style.display = 'block'
    box.classList.remove('hidden')
    content.innerHTML = step?.text || ''

    // Reset placement styles before measuring
    box.style.position = 'absolute'
    box.style.transform = 'none'
    box.style.right = 'auto'
    box.style.bottom = 'auto'

    // Place near target if available; otherwise center on screen
    if (el) {
      const rect = el.getBoundingClientRect()
      let top = window.scrollY + rect.top + rect.height + 12
      let left = window.scrollX + rect.left
      const maxLeft = window.scrollX + window.innerWidth - 340
      if (left > maxLeft) left = maxLeft
      if (!isFinite(top) || !isFinite(left)) {
        const bw = box.offsetWidth || 320
        const bh = box.offsetHeight || 200
        left = Math.max(12, window.scrollX + (window.innerWidth - bw) / 2)
        top = Math.max(12, window.scrollY + (window.innerHeight - bh) / 2)
      }
      box.style.left = left + 'px'
      box.style.top = top + 'px'
    } else {
      const bw = box.offsetWidth || 320
      const bh = box.offsetHeight || 200
      const left = Math.max(12, window.scrollX + (window.innerWidth - bw) / 2)
      const top = Math.max(12, window.scrollY + (window.innerHeight - bh) / 2)
      box.style.left = left + 'px'
      box.style.top = top + 'px'
    }
  }

  function endTour() {
    const overlay = $id(overlayId)
    const box = $id(stepId)
    if (overlay) overlay.style.display = 'none'
    box?.classList.add('hidden')
  }

  function startTour() {
    state.idx = 0
    const nextBtn = $id(nextId)
    if (nextBtn) nextBtn.textContent = 'Weiter'
    placeStep()
  }

  function attachDefaultHandlers() {
    $id(prevId)?.addEventListener('click', () => {
      state.idx = Math.max(0, state.idx - 1)
      placeStep()
    })
    $id(nextId)?.addEventListener('click', () => {
      state.idx = Math.min(state.steps.length - 1, state.idx + 1)
      placeStep()
      if (state.idx === state.steps.length - 1) {
        const btn = $id(nextId)
        if (btn) btn.textContent = 'Fertig'
        btn?.addEventListener('click', endTour, { once: true } as AddEventListenerOptions)
      }
    })
    $id(closeId)?.addEventListener('click', endTour)
    $id(neverId)?.addEventListener('click', () => { dismiss(); endTour() })
  }

  return { state, setSteps, startTour, endTour, placeStep, isDismissed, dismiss, attachDefaultHandlers }
}

<template>
  <div>
    <iframe
      ref="framerFrame"
      src="/page.html"
      style="width: 100%; height: 100vh; border: none;"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const framerFrame = ref(null)

function bindCtas(doc) {
  try {
    // Ensure CTAs are clickable and not blocked by overlays
    const ctaAnchors = Array.from(doc.querySelectorAll('a'))
      .filter(a => (a.textContent || '').toLowerCase().includes('registrieren') || (a.getAttribute('href') || '').startsWith('#'))

    // Also capture any Framer-related anchors which tend to be CTAs in exports, including login.framer.com redirects
    const framerLinks = Array.from(
      doc.querySelectorAll(
        'a[href*="framer.link"], a[href*="framer.website"], a[href*="framerusercontent.com"], a[href*="framer.com"]'
      )
    )

    const targets = [...new Set([...ctaAnchors, ...framerLinks])]

    targets.forEach(a => {
      a.style.pointerEvents = 'auto'
      a.style.cursor = 'pointer'
      a.setAttribute('role', 'button')
      a.setAttribute('tabindex', '0')
      a.addEventListener('click', (e) => {
        try {
          e.preventDefault()
          e.stopPropagation()
          // Notify parent to open auth modal
          if (window.parent) {
            window.parent.postMessage({ type: 'openSignInModal', from: 'framer-iframe' }, '*')
          }
          if (typeof window.parent?.openAuthModal === 'function') {
            window.parent.openAuthModal()
          }
        } catch {}
        return false
      }, { capture: true })
    })

    // Global capture for any remaining anchors that slip through
    try {
      doc.addEventListener('click', (evt) => {
        const target = /** @type {HTMLElement|null} */ (evt.target)
        if (!target) return
        const anchor = /** @type {HTMLAnchorElement|null} */ (target.closest('a'))
        if (!anchor) return
        const href = (anchor.getAttribute('href') || '').toLowerCase()
        if (!href) return
        if (
          href.includes('framer.link') ||
          href.includes('framer.website') ||
          href.includes('framerusercontent.com') ||
          href.includes('framer.com') ||
          href.startsWith('#')
        ) {
          evt.preventDefault()
          evt.stopPropagation()
          if (window.parent) {
            window.parent.postMessage({ type: 'openSignInModal', from: 'framer-iframe' }, '*')
          }
          if (typeof window.parent?.openAuthModal === 'function') {
            window.parent.openAuthModal()
          }
        }
      }, { capture: true })
    } catch {}

    console.log('🔗 Bound registrieren anchors:', targets.length)
  } catch (e) {
    console.warn('Failed binding CTAs in Framer iframe', e)
  }
}

function fixVisibility(doc) {
  try {
    // Make sure any full-screen overlays in export don't swallow clicks
    const blockers = doc.querySelectorAll('[data-framer-portal], [data-framer-bridge], .framer-controls, .framer-badge, #framer-badge')
    blockers.forEach(el => {
      el.style.pointerEvents = 'none'
      el.style.visibility = 'hidden'
      el.style.opacity = '0'
    })
    console.log('✅ CTA button visibility fixed')
  } catch {}
}

function onFrameLoad() {
  try {
    const iframe = framerFrame.value
    if (!iframe) return
    const doc = iframe.contentDocument || iframe.contentWindow?.document
    if (!doc) return
    console.log('🔧 Framer iframe loaded - fixing button visibility')
    fixVisibility(doc)
    bindCtas(doc)
    // Rebind when DOM changes inside iframe
    try {
      new MutationObserver(() => bindCtas(doc)).observe(doc.documentElement, { childList: true, subtree: true })
    } catch {}
  } catch {}
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    window.addEventListener('message', (event) => {
      if (event?.data?.type === 'openSignInModal') {
        // Allow reverse bridge from other frames
        if (typeof window.openAuthModal === 'function') window.openAuthModal()
      }
    })
  }
  const iframe = framerFrame.value
  if (iframe) {
    iframe.addEventListener('load', onFrameLoad)
    // If iframe already loaded before hydration, bind immediately
    try {
      const doc = iframe.contentDocument || iframe.contentWindow?.document
      if (doc && (doc.readyState === 'complete' || doc.readyState === 'interactive')) {
        onFrameLoad()
      } else {
        // Fallback: attempt after a tick
        setTimeout(onFrameLoad, 100)
      }
    } catch {}
  }
})

onBeforeUnmount(() => {
  const iframe = framerFrame.value
  if (iframe) iframe.removeEventListener('load', onFrameLoad)
})
</script>

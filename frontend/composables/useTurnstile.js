// Cloudflare Turnstile, used by the FIDE registration form. The script is
// loaded only in the browser and only once a page renders a widget, which it
// does only when the backend gives a site key (Turnstile is off otherwise).
import { ref, watch, onUnmounted } from "vue"

const SCRIPT_URL = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit"
// the form's languages, all supported by Turnstile; anything else is "auto"
const LANGUAGES = ["en", "nl", "fr"]

let scriptPromise = null

function loadScript() {
  if (window.turnstile) return Promise.resolve(window.turnstile)
  if (!scriptPromise) {
    scriptPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script")
      script.src = SCRIPT_URL
      script.async = true
      script.onload = () => resolve(window.turnstile)
      script.onerror = () => {
        scriptPromise = null
        reject(new Error("Turnstile script did not load"))
      }
      document.head.appendChild(script)
    })
  }
  return scriptPromise
}

// sitekey, element and language are refs; element is the template ref of
// the box the widget goes in. The widget follows them: it is drawn when the
// box appears, removed when it goes, and redrawn when the language changes.
export function useTurnstile({ sitekey, element, language, action }) {
  const token = ref("")
  let widgetId = null
  let generation = 0

  function remove() {
    if (widgetId !== null && window.turnstile) {
      try {
        window.turnstile.remove(widgetId)
      } catch (e) {
        // the box is already gone
      }
    }
    widgetId = null
    token.value = ""
  }

  // A token is single use and expires after 5 minutes: after a refused
  // submit or on expiry, the widget is reset for a fresh one.
  function reset() {
    token.value = ""
    if (widgetId !== null && window.turnstile) window.turnstile.reset(widgetId)
  }

  async function render() {
    const current = ++generation
    remove()
    const el = element.value
    if (!el || !sitekey.value) return
    let turnstile
    try {
      turnstile = await loadScript()
    } catch (e) {
      console.error(e.message)
      return
    }
    // a later call took over while the script loaded
    if (current !== generation) return
    widgetId = turnstile.render(el, {
      sitekey: sitekey.value,
      action,
      language: LANGUAGES.includes(language.value) ? language.value : "auto",
      theme: "light",
      size: "flexible",
      callback: (t) => {
        token.value = t
      },
      "expired-callback": () => reset(),
      "error-callback": () => {
        token.value = ""
      },
    })
  }

  watch([element, sitekey, language], render, { flush: "post" })
  onUnmounted(() => {
    generation++
    remove()
  })

  return { token, reset }
}

// stores/idbel.js
//
// The logged-in member's number, kept next to the login token (see
// idtoken.js) so it survives a reload as well.
//
// The login token carries the number as its "sub". Since the Odoo login
// (#143) nothing stored the number any more, so it stayed 0 and signing an
// interclub result card did nothing: "Signature Home: 0". The login page now
// stores it from the token, and startup() takes it from a stored token, so a
// member who was already logged in can sign without logging in again.
import { defineStore } from "pinia"
import { ref } from "vue"

const STORAGE_KEY = "idbel"
const TOKEN_KEY = "idtoken"

// The member number in a login token, or 0.
export function memberFromToken(token) {
  try {
    const payload = JSON.parse(
      atob(token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")),
    )
    const n = Number(payload.sub)
    return Number.isInteger(n) && n > 0 ? n : 0
  } catch (e) {
    return 0
  }
}

export const useIdbelStore = defineStore("idbel", () => {
  const idbel = ref(0)
  function updateIdbel(newidbel) {
    idbel.value = newidbel
    try {
      if (newidbel) window.localStorage.setItem(STORAGE_KEY, String(newidbel))
      else window.localStorage.removeItem(STORAGE_KEY)
    } catch (e) {
      // storage blocked: memory only
    }
  }
  function startup() {
    if (idbel.value) return
    try {
      // the stored token is who is logged in; the stored number may be
      // left over from an earlier login
      const fromToken = memberFromToken(window.localStorage.getItem(TOKEN_KEY) || "")
      if (fromToken) {
        updateIdbel(fromToken)
        return
      }
      const stored = window.localStorage.getItem(STORAGE_KEY)
      if (stored) idbel.value = Number(stored)
    } catch (e) {
      // storage blocked
    }
  }
  return { idbel, updateIdbel, startup }
})

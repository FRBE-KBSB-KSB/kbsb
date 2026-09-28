// stores/idbel.js
//
// The logged-in member's number, kept next to the login token (see
// idtoken.js) so it survives a reload as well.
import { defineStore } from "pinia"
import { ref } from "vue"

const STORAGE_KEY = "idbel"

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
      const stored = window.localStorage.getItem(STORAGE_KEY)
      if (stored) idbel.value = Number(stored)
    } catch (e) {
      // storage blocked
    }
  }
  return { idbel, updateIdbel, startup }
})

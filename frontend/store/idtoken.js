// stores/idtoken.js
//
// The member login token (Odoo login). Kept in localStorage so a reload or a
// new visit does not ask for the login again: it used to be held in memory
// only (startup() read a key nothing ever wrote), so every page load meant
// signing in again. The token expires on the server after its own timeout;
// an expired one is dropped here instead of being sent.
import { defineStore } from "pinia";
import { ref } from "vue";

const STORAGE_KEY = "idtoken";

function expired(token) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")));
    return typeof payload.exp === "number" && payload.exp * 1000 <= Date.now();
  } catch (e) {
    return true;
  }
}

export const useIdtokenStore = defineStore("idtoken", () => {
  const token = ref(null);
  function updateToken(newtoken) {
    token.value = newtoken;
    try {
      if (newtoken) window.localStorage.setItem(STORAGE_KEY, newtoken);
      else window.localStorage.removeItem(STORAGE_KEY);
    } catch (e) {
      // storage blocked (private window, embedded page): memory only
    }
  }
  function startup() {
    if (token.value) return;
    let stored = null;
    try {
      stored = window.localStorage.getItem(STORAGE_KEY);
    } catch (e) {
      return;
    }
    if (stored && !expired(stored)) token.value = stored;
    else if (stored) updateToken(null);
  }
  return { token, updateToken, startup };
});

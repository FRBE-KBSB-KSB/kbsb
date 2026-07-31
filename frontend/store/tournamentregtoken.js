// stores/tournamentregtoken.js
//
// Auth store for the "Tournament Registrations" feature only. This is a
// completely separate, self-contained identity system (arbiter/organizer
// username+password -> JWT from POST /admin/login on the tournament
// registrations backend) that has nothing to do with the site's mgmt
// Google-auth staff login (store/mgmttoken.js + store/person.js) -- do not
// merge or share state with those.
//
// Shape mirrors store/mgmttoken.js (ref + updateToken + startup), but
// updateToken here also persists to localStorage under its own key: in
// mgmttoken.js that never actually happens (startup() there reads a
// differently-named key than updateToken ever writes), which would leave
// this feature's session unable to survive a page reload. Since this store
// has no other system seeding localStorage for it, updateToken has to do it.
import { defineStore } from "pinia";
import { ref } from "vue";

const STORAGE_KEY = "tournamentregtoken";

export const useTournamentRegTokenStore = defineStore("tournamentregtoken", () => {
  const token = ref(null);
  function updateToken(newtoken) {
    token.value = newtoken;
    if (newtoken) {
      window.localStorage.setItem(STORAGE_KEY, newtoken);
    } else {
      window.localStorage.removeItem(STORAGE_KEY);
    }
  }
  function startup() {
    if (!token.value) {
      token.value = window.localStorage.getItem(STORAGE_KEY);
    }
  }
  return { token, updateToken, startup };
});

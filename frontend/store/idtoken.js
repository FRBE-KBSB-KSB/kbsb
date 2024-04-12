// stores/idtoken.js
import { defineStore } from "pinia";
import { ref } from "vue";

export const useIdtokenStore = defineStore("idtoken", () => {
  const token = ref(null);
  function updateToken(newtoken) {
    token.value = newtoken;
  }
  function startup() {
    if (!token.value) {
      token.value = window.localStorage.getItem("idtoken");
    }
  }
  return { token, updateToken, startup };
});

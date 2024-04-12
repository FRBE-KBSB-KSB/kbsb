// stores/mgmttoken.js
import { defineStore } from "pinia";
import { ref } from "vue";

export const useMgmtInterclubStore = defineStore("mgmtinterclub", () => {
  const club = ref({});
  const round = ref(0)
  function updateClub(newclub) {
    club.value = newclub;
  }
  function updateRound(newround) {
    round.value = newround;
  }
  return { club, round, updateClub, updateRound };
});

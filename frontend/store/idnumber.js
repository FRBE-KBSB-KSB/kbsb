// stores/idnumber.js
import { defineStore } from "pinia";
import { ref } from "vue";

export const useIdnumberStore = defineStore("idnumber", () => {
  const idnumber = ref(0);
  function updateIdnumber(newnumber) {
    idnumber.value = newnumber;
  }
  return { idnumber, updateIdnumber };
});

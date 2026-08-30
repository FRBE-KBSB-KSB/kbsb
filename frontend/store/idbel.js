// stores/idbel.js
import { defineStore } from "pinia"
import { ref } from "vue"

export const useIdbelStore = defineStore("idbel", () => {
  const idbel = ref(0)
  function updateIdbel(newidbel) {
    idbel.value = newidbel
  }
  return { idbel, updateIdbel }
})

function saveToLs(state) {
  window.localStorage.setItem("newlogin", state.value)
}

function readFromLs(state) {
  if (!state.value) {
    const newlogin = window.localStorage.getItem("newlogin")
    if (newlogin) {
      state.value = newlogin
    }
  }
}


export const state = () => ({
  value: ''
})

export const mutations = {
  startup(state) {
    readFromLs(state)
  },
  update(state, payload) {
    console.log('Updating newlogin', payload)
    state.value = payload
    saveToLs(state)
  }
}

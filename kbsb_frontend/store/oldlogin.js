function saveToLs(state) {
  window.localStorage.setItem("oldlogin",state.value)
}

function readFromLs(state) {
  if (!state.value) {
    const oldlogin = window.localStorage.getItem("oldlogin")
    if (oldlogin) {
      state.value = oldlogin
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
  update (state, payload) {
    console.log('Updating oldlogin', payload)
    state.value = payload
    saveToLs(state)
  }
}

export const state = () => ({
  value: ''
})

export const mutations = {
  update (state, payload) {
    console.log('Updating oldlogin', payload)
    state.value = payload
  }
}

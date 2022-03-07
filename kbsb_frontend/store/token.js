export const state = () => ({
  value: ''
})

export const mutations = {
  update (state, payload) {
    console.log('update token', payload)
    state.value = payload
  }
}

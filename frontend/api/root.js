export default context => ({
  async root() {
    return await context.$axios.get('/api')
  },
  async login(options) {
    return await context.$axios.post('/api/v1/accounts/login', options)
  }
})

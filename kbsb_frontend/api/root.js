export default context => ({
  async root () {
    return await context.$axios.get('/api')
  },
  async login (options) {
    return await await context.$axios.post('/api/v1/login', options)
  }
})

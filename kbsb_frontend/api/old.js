export default context => ({
  async login(options) {
    return await context.$axios.post('/api/v1/old/login', options)
  },
  async get_clubmembers(options) {
    const { idclub } = options
    return await context.$axios.get(`/api/v1/old/clubmembers/${idclub}`)
  },
})

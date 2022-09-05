export default context => ({
  async login(options) {
    return await context.$axios.post('/api/v1/old/login', options)
  },
  async get_clubmembers(options) {
    console.log('api get_clubmembers')
    const { idclub } = options
    return await context.$axios.get(`/api/v1/old/clubmembers/${idclub}`)
  },
  async get_member(options) {
    console.log('api get_member')
    const { idnumber } = options
    return await context.$axios.get(`/api/v1/old/activemember/${idnumber}`)
  },
})

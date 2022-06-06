export default context => ({
    async login(options) {
      return await await context.$axios.post('/api/v1/old/login', options)  
    }
  })
  
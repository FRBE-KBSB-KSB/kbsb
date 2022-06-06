export default context => ({
  async add_club (options) {
    const { token, ...options1 } = options
    console.log('add club', options1, token)
    const resp = await context.$axios.post('/api/v1/club', options1, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async delete_club (options) {
    const { id, token } = options
    const resp = await context.$axios.delete(`/api/v1/club/${id}`, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async get_club (options) {
    const { id, token } = options
    const resp = await context.$axios.get(`/api/v1/club/${id}`, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async get_anon_club (options) {
    const { id} = options
    const resp = await context.$axios.get(`/api/v1/a/club/${id}`, {
    })
    return resp
  },
  async get_clubs (options) {
    const { token } = options
    console.log('api get_clubs', token)
    const resp = await context.$axios.get('/api/v1/clubs', {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async get_old_clubs (options) {
    const { token } = options
    console.log('api get_old_clubs', token)
    const resp = await context.$axios.get('/api/v1/c/clubs', {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async get_anon_clubs (options) {
    const resp = await context.$axios.get('/api/v1/a/clubs')
    return resp
  },
  async update_club (options) {
    const { id, token, ...options1 } = options
    const resp = await context.$axios.put(`/api/v1/club/${id}`, options1, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  }
})

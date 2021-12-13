export default context => ({
  anon_get_files (options) {
    const { reports, ...options1 } = options
    console.log('inside anon_get_files', reports, options1)
    return context.$axios.get('/api/a/files', { params: { reports } })
  },
  async add_file (options) {
    const { token, ...options1 } = options
    console.log('add file', options1, token)
    const resp = await context.$axios.post('/api/files', options1, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async delete_file (options) {
    const { id, token } = options
    const resp = await context.$axios.delete(`/api/file/${id}`, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async get_file (options) {
    const { id, token } = options
    const resp = await context.$axios.get(`/api/file/${id}`, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async get_files (options) {
    const { token } = options
    const resp = await context.$axios.get('/api/files', {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async update_file (options) {
    const { id, token, ...options1 } = options
    const resp = await context.$axios.put(`/api/file/${id}`, options1, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  }

})

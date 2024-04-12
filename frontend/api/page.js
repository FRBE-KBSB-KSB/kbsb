export default context => ({
  anon_slug_page (options) {
    const { slug, ...options1 } = options
    return context.$axios.get(`/api/v1/a/slug/${slug}`, options1)
  },
  async add_page (options) {
    const { token, ...options1 } = options
    console.log('add page', options1, token)
    const resp = await context.$axios.post('/api/v1/page', options1, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async delete_page (options) {
    const { id, token } = options
    const resp = await context.$axios.delete(`/api/v1/page/${id}`, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async get_page (options) {
    const { id, token } = options
    const resp = await context.$axios.get(`/api/v1/page/${id}`, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async get_pages (options) {
    const { token } = options
    const resp = await context.$axios.get('/api/v1/pages', {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async update_page (options) {
    const { id, token, ...options1 } = options
    const resp = await context.$axios.put(`/api/v1/page/${id}`, options1, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async get_anon_articles (options) {
    const resp = await context.$axios.get('/api/v1/a/articles')
    return resp
  },
  async get_ic_announcements (options) {
    const resp = await context.$axios.get('/api/v1/a/ic_announcements')
    return resp
  },
})

export default (context) => ({
  get_pages(options) {
    const { authorization, ...options1 } = options
    return context.$axios.get('/api/pages', {
      headers: { Authorization: authorization },
      ...options1,
    })
  },
  anon_get_pages() {
    return context.$axios.get('/api/a/pages')
  },
  backup_pages(options) {
    const { authorization, ...options1 } = options
    return context.$axios.get('/api/pages/backup', {
      headers: { Authorization: authorization },
      ...options1,
    })
  },
  restore_pages(options) {
    const { authorization, ...options1 } = options
    return context.$axios.get('/api/pages/restore', {
      headers: { Authorization: authorization },
      ...options1,
    })
  },
  add_page(options) {
    const { authorization, pagein, ...options1 } = options
    return context.$axios.post('/api/page', pagein, {
      headers: { Authorization: authorization },
      ...options1,
    })
  },
  get_page(options) {
    const { authorization, pageId, ...options1 } = options
    return context.$axios.post(`/api/page/${pageId}`, {
      headers: { Authorization: authorization },
      ...options1,
    })
  },
  anon_get_page(options) {
    const { pageId, ...options1 } = options
    return context.$axios.get(`/api/a/page/${pageId}`, options1)
  },
  anon_get_page_by_slug(options) {
    const { slug, ...options1 } = options
    return context.$axios.get(`/api/a/pages/slug/${slug}`, options1)
  },
})

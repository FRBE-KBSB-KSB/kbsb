export default context => ({
  anon_slug_page (options) {
    const { slug, ...options1 } = options
    console.log('inside anon_slug_page', slug, options1)
    return context.$axios.get(`/api/a/slug/${slug}`, options1)
  }
})

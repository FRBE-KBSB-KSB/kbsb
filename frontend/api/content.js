export default (context) => ({
  anon_get_content(options) {
    const { slug } = options
    return context.$axios.get(`/api/a/pages/slug/${slug}`)
  },
  getActiveArticles(){
    return context.$axios.get(`/api/a/articles`)
  }
})

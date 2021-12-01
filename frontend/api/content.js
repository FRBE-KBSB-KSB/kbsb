export default context => ({
  getActiveArticles () {
    return context.$axios.get('/api/a/articles')
  }
})

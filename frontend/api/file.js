export default context => ({
  anon_get_files (options) {
    const { reports, ...options1 } = options
    console.log('inside anon_get_files', reports, options1)
    return context.$axios.get('/api/a/files', { params: { reports } })
  }
})

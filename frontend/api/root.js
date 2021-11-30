export default context => ({
  root() {
    console.log('calling axios', context.$config, context.$axios)
    return context.$axios.get('/api')
  }
})

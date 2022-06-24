export default context => ({
  async anon_get_enrollment (options) {
    const { idclub } = options
    const resp = await context.$axios.get(`/api/v1/a/interclub/enrollment/${idclub}`)
    return resp
  },
  async make_enrollment (options) {
    const { token, ...enrollment } = options
    const resp = await context.$axios.post('/api/v1/c/interclub/enrollment', enrollment, {
      headers: {
        Authorization: 'Bearer ' + token
      }
  })
    return resp
  },
})

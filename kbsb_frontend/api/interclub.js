export default context => ({
  async anon_get_enrollment(options) {
    console.log('api anon_get_enrollment')
    const { idclub } = options
    const resp = await context.$axios.get(`/api/v1/a/interclub/enrollment/${idclub}`)
    return resp
  },
  async make_enrollment(options) {
    const { token, ...enrollment } = options
    const resp = await context.$axios.post('/api/v1/c/interclub/enrollment', enrollment, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async update_enrollment(options) {
    console.log('api update_enrollment')
    const { token, idclub, ...enrollment } = options
    const resp = await context.$axios.put(`/api/v1/c/interclub/enrollment/${idclub}`,
      enrollment, { headers: { Authorization: 'Bearer ' + token } }
    )
    return resp
  },
})

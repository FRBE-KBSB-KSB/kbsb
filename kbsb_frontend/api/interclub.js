export default context => ({
  async find_interclubenrollment(options) {
    console.log('api anon_get_enrollment')
    const { idclub } = options
    const resp = await context.$axios.get(`/api/v1/a/interclub/enrollment/${idclub}`)
    return resp
  },
  async set_interclubenrollment(options) {
    const { token, idclub, ...enrollment } = options
    const resp = await context.$axios.post(`/api/v1/c/interclub/enrollment/${idclub}`, enrollment, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async mgmt_set_interclubenrollment(options) {
    const { token, idclub, ...enrollment } = options
    const resp = await context.$axios.post(`/api/v1/interclub/enrollment/${idclub}`, enrollment, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async mgmt_csv_interclubenrollment(options) {
    const { token } = options
    const resp = await context.$axios.get(`/api/v1/csv/interclubenrollment`, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async find_interclubvenues(options) {
    const { token, idclub } = options
    const resp = await context.$axios.get(`/api/v1/a/interclub/venues/${idclub}`)
    return resp
  },
  async set_interclubvenues(options) {
    const { token, idclub, venues } = options
    const resp = await context.$axios.post(`/api/v1/c/interclub/venues/${idclub}`,
      { venues }, { headers: { Authorization: 'Bearer ' + token } }
    )
    return resp
  },
  async mgmt_set_interclubvenues(options) {
    const { token, idclub, venues } = options
    const resp = await context.$axios.post(`/api/v1/interclub/venues/${idclub}`,
      { venues }, { headers: { Authorization: 'Bearer ' + token } }
    )
    return resp
  },
  async mgmt_csv_interclubvenues(options) {
    const { token } = options
    const resp = await context.$axios.get(`/api/v1/csv/interclubvenues`, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
})

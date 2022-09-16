export default context => ({
  async find_interclubenrollment(options) {
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
  async get_interclubclub(options) {
    const { idclub } = options
    const resp = await context.$axios.get(`/api/v1/a/interclub/club/${idclub}`)
    return resp
  },
  async mgmt_set_interclubclub(options) {
    console.log('api mgmt_set_interclubclub', options)
    const { token, idclub, ...icc } = options
    const resp = await context.$axios.put(`/api/v1/interclub/club/${idclub}`,
      icc, { headers: { Authorization: 'Bearer ' + token } }
    )
    return resp
  },
  async clb_set_interclubclub(options) {
    console.log('api clb_set_interclubclub', options)
    const { token, idclub, ...icc } = options
    const resp = await context.$axios.put(`/api/v1/c/interclub/club/${idclub}`,
      icc, { headers: { Authorization: 'Bearer ' + token } }
    )
    return resp
  },
  async get_announcements() {
    console.log('api annoucements')
    const resp = await context.$axios.get('/api/v1/a/interclub/announcements')
    return resp
  },
})

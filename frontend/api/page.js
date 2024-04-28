import axios from 'axios'

const prefix = '/api/v1/page'

export default {
  copyarticles: async function (options) {
    const { token } = options
    return await axios.post(`${prefix}/checkout/articles`, {}, {
      headers: {
        Authorization: "Bearer " + token,
      }
    })
  },
  copypages: async function (options) {
    const { token } = options
    return await axios.post(`${prefix}/checkout/pages`, {}, {
      headers: {
        Authorization: "Bearer " + token,
      }
    })
  },
}

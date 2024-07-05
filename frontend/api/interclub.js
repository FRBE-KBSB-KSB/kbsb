import axios from "axios"

const prefix = "/api/v1/interclubs"

export default {
  // enrollemnts
  find_interclubenrollment: async function (options) {
    const { idclub } = options
    const resp = await axios.get(`${prefix}/anon/enrollment/${idclub}`)
    return resp
  },
  set_interclubenrollment: async function (options) {
    const { token, idclub, ...enrollment } = options
    const resp = await axios.post(
      `${prefix}/clb/enrollment/${idclub}`,
      enrollment,
      {
        headers: {
          Authorization: "Bearer " + token,
        },
      }
    )
    return resp
  },
  mgmt_set_interclubenrollment: async function (options) {
    const { token, idclub, ...enrollment } = options
    const resp = await axios.post(
      `${prefix}/mgmt/enrollment/${idclub}`,
      enrollment,
      {
        headers: {
          Authorization: "Bearer " + token,
        },
      }
    )
    return resp
  },
  mgmt_xls_icregistrations: async function (options) {
    const { token } = options
    const resp = await axios.get(`${prefix}/mgmt/command/xls_registrations`, {
      headers: {
        Authorization: "Bearer " + token,
      },
    })
    return resp
  },

  //venues
  anon_getICVenues: async function (options) {
    const { token, idclub } = options
    const resp = await axios.get(`${prefix}/anon/venue/${idclub}`)
    return resp
  },
  set_interclubvenues: async function (options) {
    const { token, idclub, venues } = options
    const resp = await axios.post(
      `${prefix}/clb/venue/${idclub}`,
      { venues },
      { headers: { Authorization: "Bearer " + token } }
    )
    return resp
  },
  mgmt_set_interclubvenues: async function (options) {
    const { token, idclub, venues } = options
    const resp = await axios.post(
      `${prefix}/mgmt/venue/${idclub}`,
      { venues },
      { headers: { Authorization: "Bearer " + token } }
    )
    return resp
  },
  mgmt_csv_interclubvenues: async function (options) {
    const { token } = options
    const resp = await axios.get(`${prefix}/mgmt/command/exportvenues`, {
      headers: {
        Authorization: "Bearer " + token,
      },
    })
    return resp
  },

  // icclub
  anon_getICteams: async function (options) {
    const { idclub } = options
    const resp = await axios.get(`${prefix}/anon/icteams/${idclub}`)
    return resp
  },
  anon_getICclub: async function (options) {
    const { idclub } = options
    const resp = await axios.get(`${prefix}/anon/icclub/${idclub}`)
    return resp
  },
  anon_getICclubs: async function () {
    const resp = await axios.get(`${prefix}/anon/icclub`)
    return resp
  },
  clb_getICclub: async function (options) {
    const { token, idclub } = options
    const resp = await axios.get(`${prefix}/clb/icclub/${idclub}`, {
      headers: {
        Authorization: "Bearer " + token,
      },
    })
    return resp
  },
  mgmt_getICclub: async function (options) {
    const { token, idclub } = options
    const resp = await axios.get(`${prefix}/mgmt/icclub/${idclub}`, {
      headers: {
        Authorization: "Bearer " + token,
      },
    })
    return resp
  },
  clb_setICclub: async function (options) {
    console.log("api clb_setICclub", options)
    const { token, idclub, ...icc } = options
    const resp = await axios.put(`${prefix}/clb/icclub/${idclub}`, icc, {
      headers: { Authorization: "Bearer " + token },
    })
    return resp
  },
  mgmt_setICclub: async function (options) {
    console.log("api clb_setICclub", options)
    const { token, idclub, ...icc } = options
    const resp = await axios.put(`${prefix}/mgmt/icclub/${idclub}`, icc, {
      headers: { Authorization: "Bearer " + token },
    })
    return resp
  },
  clb_validateICplayers: async function (options) {
    const { token, idclub, players } = options
    const resp = await axios.post(
      `${prefix}/clb/icclub/${idclub}/validate`,
      { players },
      {
        headers: { Authorization: "Bearer " + token },
      }
    )
    return resp
  },
  mgmt_validateICplayers: async function (options) {
    const { token, idclub, players } = options
    const resp = await axios.post(
      `${prefix}/mgmt/icclub/${idclub}/validate`,
      { players },
      {
        headers: { Authorization: "Bearer " + token },
      }
    )
    return resp
  },
  mgmt_getXlsAllplayerlists: async function (options) {
    const { token } = options
    const resp = await axios.get(`${prefix}/mgmt/command/xls/allplayerlist`, {
      headers: { Authorization: "Bearer " + token },
    })
    return resp
  },

  // results and pairings
  anon_getICseries: async function (options) {
    const { idclub, round } = options
    const resp = await axios.get(`${prefix}/anon/icseries`, {
      params: { idclub, round },
    })
    return resp
  },
  clb_getICseries: async function (options) {
    const { token, idclub, round } = options
    const resp = await axios.get(`${prefix}/clb/icseries`, {
      headers: { Authorization: "Bearer " + token },
      params: { idclub, round },
    })
    return resp
  },
  mgmt_getICseries: async function (options) {
    const { token, idclub, round } = options
    const resp = await axios.get(`${prefix}/mgmt/icseries`, {
      headers: { Authorization: "Bearer " + token },
      params: { idclub, round },
    })
    return resp
  },
  clb_saveICplanning: async function (options) {
    const { token, ...option } = options
    const resp = await axios.put(`${prefix}/clb/icplanning`, options, {
      headers: { Authorization: "Bearer " + token },
    })
    return resp
  },
  mgmt_saveICresults: async function (options) {
    const { token, ...option } = options
    const resp = await axios.put(`${prefix}/mgmt/icresults`, options, {
      headers: { Authorization: "Bearer " + token },
    })
    return resp
  },
  clb_saveICresults: async function (options) {
    const { token, ...option } = options
    console.log("api options", options)
    const resp = await axios.put(`${prefix}/clb/icresults`, options, {
      headers: { Authorization: "Bearer " + token },
    })
    return resp
  },
  anon_getICencounterdetails: async function (options) {
    const resp = await axios.get(`${prefix}/anon/icresultdetails`, {
      params: options,
    })
    return resp
  },
  anon_getICstandings: async function (options) {
    const { idclub } = options
    const resp = await axios.get(`${prefix}/anon/icstandings`, {
      params: { idclub },
    })
    return resp
  },
  mgmt_generate_bel_elo: async function (options) {
    const { token, round } = options
    const resp = await axios.post(
      `${prefix}/mgmt/command/belg_elo`,
      {},
      {
        headers: { Authorization: "Bearer " + token },
        params: { round },
      }
    )
    return resp
  },
  mgmt_generate_fide_elo: async function (options) {
    const { token, round } = options
    const resp = await axios.post(
      `${prefix}/mgmt/command/fide_elo`,
      {},
      {
        headers: { Authorization: "Bearer " + token },
        params: { round },
      }
    )
    return resp
  },
  mgmt_generate_penalties: async function (options) {
    const { token, round } = options
    const resp = await axios.post(
      `${prefix}/mgmt/command/penalties/${round}`, {},
      { headers: { Authorization: "Bearer " + token } }
    )
    return resp
  },
  mgmt_register_teamforfeit: async function (options) {
    const { token, division, index, name } = options
    const resp = await axios.post(
      `${prefix}/mgmt/command/teamforfeit/${division}/${index}/${name}`,
      {},
      {
        headers: { Authorization: "Bearer " + token },
      }
    )
    return resp
  },

}

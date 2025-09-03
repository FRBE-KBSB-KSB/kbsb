import axios from "axios"

const prefix = "/api/v1/interclubs"

export default {
  // registrations
  find_interclubregistration: async function (options) {
    const { idclub } = options
    const resp = await axios.get(`${prefix}/anon/registration/${idclub}`)
    return resp
  },
  set_interclubregistration: async function (options) {
    const { token, idclub, ...registration } = options
    const resp = await axios.post(
      `${prefix}/clb/registration/${idclub}`,
      registration,
      {
        headers: {
          Authorization: "Bearer " + token,
        },
      }
    )
    return resp
  },
  mgmt_set_interclubregistration: async function (options) {
    const { token, idclub, ...registration } = options
    const resp = await axios.post(
      `${prefix}/mgmt/registration/${idclub}`,
      registration,
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
    const { idclub } = options
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
  mgmt_xls_icvenues: async function (options) {
    const { token } = options
    const resp = await axios.get(`${prefix}/mgmt/command/xls_venues`, {
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
    console.log("api mgmt_getICclub", options)
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
  anon_xls_playerlist: async function (options) {
    const { idclub } = options
    const resp = await axios.get(
      `${prefix}/anon/command/xls_playerlist/${idclub}`
    )
    return resp
  },
  mgmt_xls_playerlists: async function (options) {
    const { token } = options
    const resp = await axios.get(`${prefix}/mgmt/command/xls_playerlists`, {
      headers: {
        Authorization: "Bearer " + token,
      },
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
  anon_getICStandingsArchive: async function (options) {
    const { season } = options
    const resp = await axios.get(`${prefix}/anon/icstandingsarchive`, {
      params: { season },
    })
    return resp
  },
  anon_getICResultsArchive: async function (options) {
    const { season, round } = options
    console.log("api anon_getICResultsArchive", season, round)
    const resp = await axios.get(`${prefix}/anon/icresultsarchive`, {
      params: { season, round },
    })
    return resp
  },
  mgmt_generate_penalties: async function (options) {
    const { token, round } = options
    const resp = await axios.post(
      `${prefix}/mgmt/command/penalties/${round}`,
      {},
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

  // elo and penalties reporting
  mgmt_list_eloprocessing: async function (options) {
    const { token } = options
    const resp = await axios.post(
      `${prefix}/mgmt/command/list_eloprocessing`,
      {},
      {
        headers: { Authorization: "Bearer " + token },
      }
    )
    return resp
  },
  mgmt_write_eloprocessing: async function (options) {
    const { token } = options
    const resp = await axios.post(
      `${prefix}/mgmt/command/write_eloprocessing`,
      {},
      {
        headers: { Authorization: "Bearer " + token },
      }
    )
    return resp
  },
  mgmt_write_bel_report: async function (options) {
    const { token, round, path_elo } = options
    const resp = await axios.post(
      `${prefix}/mgmt/command/write_bel_report/${round}/${path_elo}`,
      {},
      {
        headers: { Authorization: "Bearer " + token },
      }
    )
    return resp
  },
  mgmt_write_fide_report: async function (options) {
    const { token, round, path_elo } = options
    const resp = await axios.post(
      `${prefix}/mgmt/command/write_fide_report/${round}/${path_elo}`,
      {},
      {
        headers: { Authorization: "Bearer " + token },
      }
    )
    return resp
  },
  list_bel_reports: async function (options) {
    const { token } = options
    const resp = await axios.post(
      `${prefix}/mgmt/command/list_bel_reports`,
      {},
      {
        headers: { Authorization: "Bearer " + token },
      }
    )
    return resp
  },
  list_fide_reports: async function (options) {
    const { token } = options
    const resp = await axios.post(
      `${prefix}/mgmt/command/list_fide_reports`,
      {},
      {
        headers: { Authorization: "Bearer " + token },
      }
    )
    return resp
  },
  get_bel_report: async function (options) {
    const { token, path } = options
    const resp = await axios.get(
      `${prefix}/mgmt/command/get_bel_report/${path}`,
      {
        headers: { Authorization: "Bearer " + token },
      }
    )
    return resp
  },
  get_fide_report: async function (options) {
    const { token, path } = options
    const resp = await axios.get(
      `${prefix}/mgmt/command/get_fide_report/${path}`,
      {
        headers: { Authorization: "Bearer " + token },
      }
    )
    return resp
  },
  write_penalties_report: async function (options) {
    const { token, round } = options
    const resp = await axios.post(
      `${prefix}/mgmt/command/write_penalties_report/${round}`,
      {},
      {
        headers: { Authorization: "Bearer " + token },
      }
    )
    return resp
  },
  list_penalties_reports: async function (options) {
    const { token } = options
    const resp = await axios.post(
      `${prefix}/mgmt/command/list_penalties_reports`,
      {},
      {
        headers: { Authorization: "Bearer " + token },
      }
    )
    return resp
  },
  get_penalties_report: async function (options) {
    const { token, path } = options
    const resp = await axios.get(
      `${prefix}/mgmt/command/get_penalties_report/${path}`,
      {
        headers: { Authorization: "Bearer " + token },
      }
    )
    return resp
  },
  icdata: async function (options) {
    const resp = await axios.get(`${prefix}/icdata`)
    return resp
  }
}

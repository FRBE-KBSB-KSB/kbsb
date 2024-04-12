import axios from "axios";

const prefix = "/api/v1/clubs";
export default {
  // mgmt nethods

  mgmt_add_club: async function (options) {
    const { token, ...options1 } = options;
    console.log("add club", options1, token);
    const resp = await axios.post(`${prefix}/mgmt/club`, options1, {
      headers: {
        Authorization: "Bearer " + token,
      },
    });
    return resp;
  },
  mgmt_get_club: async function (options) {
    const { idclub, token } = options;
    const resp = await axios.get(`${prefix}/mgmt/club/${idclub}`, {
      headers: {
        Authorization: "Bearer " + token,
      },
    });
    return resp;
  },
  mgmt_delete_club: async function (options) {
    const { idclub, token } = options;
    const resp = await axios.delete(`${prefix}/mgmt/club/${idclub}`, {
      headers: {
        Authorization: "Bearer " + token,
      },
    });
    return resp;
  },
  mgmt_update_club: async function (options) {
    const { idclub, token, ...options1 } = options;
    const resp = await axios.put(`${prefix}/mgmt/club/${idclub}`, options1, {
      headers: {
        Authorization: "Bearer " + token,
      },
    });
    return resp;
  },

  // clb nethods

  clb_get_club: async function (options) {
    const { idclub, token } = options;
    const resp = await axios.get(`${prefix}/clb/club/${idclub}`, {
      headers: {
        Authorization: "Bearer " + token,
      },
    });
    return resp;
  },
  clb_get_clubs: async function (options) {
    const { token } = options;
    console.log("api get_old_clubs", token);
    const resp = await axios.get("/api/v1/c/clubs", {
      headers: {
        Authorization: "Bearer " + token,
      },
    });
    return resp;
  },
  clb_update_club: async function (options) {
    const { idclub, token, ...options1 } = options;
    const resp = await axios.put(`${prefix}/clb/club/${idclub}`, options1, {
      headers: {
        Authorization: "Bearer " + token,
      },
    });
    return resp;
  },

  // anon nethods

  anon_get_club: async function (options) {
    const { idclub } = options;
    const resp = await axios.get(`${prefix}/anon/club/${idclub}`, {});
    return resp;
  },
  anon_get_clubs: async function (options) {
    const resp = await axios.get(`${prefix}/anon/club/`);
    return resp;
  },
  anon_get_csv_clubs: async function (options) {
    const resp = await axios.get(`${prefix}/anon/csvclubs/`);
    return resp;
  },

  // other
  verify_club_access: async function (options) {
    const { idclub, token, role } = options;
    const resp = await axios.get(
      `${prefix}/clb/club/${idclub}/access/${role}`,
      {
        headers: {
          Authorization: "Bearer " + token,
        },
      }
    );
    return resp;
  },
};

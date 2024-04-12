import axios from "axios";

const prefix = "/api/v1/member";
export default {
  login: async function (options) {
    return await axios.post(`${prefix}/login`, options);
  },
  anon_getclubmembers: async function (options) {
    const { idclub } = options;
    return await axios.get(`${prefix}/anon/clubmembers/${idclub}`);
  },
  mgmt_getclubmembers: async function (options) {
    const { token, idclub } = options;
    return await axios.get(`${prefix}/mgmt/clubmembers/${idclub}`, {
      headers: {
        Authorization: "Bearer " + token,
      },
    });
  },
  anon_getmember: async function (options) {
    const { idnumber } = options;
    return await axios.get(`${prefix}/anon/member/${idnumber}`);
  },
  mgmtlogin: async function (options) {
    return await axios.get(`${prefix}/mgmt/login`, options);
  },
};

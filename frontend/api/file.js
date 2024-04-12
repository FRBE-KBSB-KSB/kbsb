import axios from "axios";

const rprefix = "/api/v1/report";
const fprefix = "/api/v1/filestore";

export default {
  anon_get_files: async function (options) {
    const { reports } = options;
    return await axios.get(`${rprefix}/anon/file`, {
      params: { reports },
    });
  },
  add_file: async function (options) {
    const { token, ...options1 } = options;
    console.log("add file", options1, token);
    const resp = await axios.post("/api/v1/files", options1, {
      headers: {
        Authorization: "Bearer " + token,
      },
    });
    return resp;
  },
  delete_file: async function (options) {
    const { id, token } = options;
    const resp = await axios.delete(`/api/v1/file/${id}`, {
      headers: {
        Authorization: "Bearer " + token,
      },
    });
    return resp;
  },
  get_file: async function (options) {
    const { id, token } = options;
    const resp = await axios.get(`/api/v1/file/${id}`, {
      headers: {
        Authorization: "Bearer " + token,
      },
    });
    return resp;
  },
  get_files: async function (options) {
    const { token } = options;
    const resp = await axios.get("/api/v1/files", {
      headers: {
        Authorization: "Bearer " + token,
      },
    });
    return resp;
  },
  update_file: async function (options) {
    const { id, token, ...options1 } = options;
    const resp = await axios.put(`/api/v1/file/${id}`, options1, {
      headers: {
        Authorization: "Bearer " + token,
      },
    });
    return resp;
  },
  anon_get_file: async function (options) {
    const { group, name } = options
    return await axios.get(`${fprefix}/anon/file`, {
      params: { group, name },
    })
  },
  anon_get_filelist: async function (options) {
    const { group } = options
    return await axios.get(`${fprefix}/anon/files`, {
      params: { group },
    })
  },
};

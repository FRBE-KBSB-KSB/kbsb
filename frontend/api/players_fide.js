import axios from "axios";

const prefix = "/api/v1/players_fide";

export default {
  async search(options) {
    const qEscaped = encodeURIComponent((options && options.q) ? options.q.trim() : "");
    return await axios.get(`${prefix}/search?q=${qEscaped}`);
  },
  async lookup(options) {
    const id = (options && options.fide_id) ? options.fide_id : "";
    return await axios.get(`${prefix}/${id}`);
  }
};

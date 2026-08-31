import axios from "axios";

const prefix = "/api/v1/arbiters";

export default {
  async search(options) {
    const q = (options && options.q) ? options.q.trim() : "";
    const fed = (options && options.fed) ? options.fed.trim() : "";
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (fed) params.set("fed", fed);
    const config = {};
    if (options && options.signal) config.signal = options.signal;
    return await axios.get(`${prefix}/search?${params.toString()}`, config);
  },
  async lookup(options) {
    const id = (options && options.fide_id) ? options.fide_id : "";
    return await axios.get(`${prefix}/${id}`);
  }
};

import axios from "axios";

// Relative path resolved against axios.defaults.baseURL (set from
// runtimeConfig.public.apiUrl in plugins/backend.js), same as every other
// api/*.js client. A hardcoded absolute "http://127.0.0.1:8000" here used to
// dodge Node 18+ SSR resolving "localhost" to IPv6 in local dev, but it also
// ignored API_URL in production, sending deployed users' browsers to their
// own machine instead of the real backend. The shared apiUrl default is
// already the IPv4 literal ("http://127.0.0.1:8000/"), so this relative path
// avoids the IPv6 issue locally while still respecting API_URL when deployed.
const prefix = "/api/v1/national_elo_archive";

export default {
  async search(options) {
    const qEscaped = encodeURIComponent((options && options.q) ? options.q.trim() : "");
    const typeQuery = (options && options.type) ? `&type=${encodeURIComponent(options.type)}` : "";
    return await axios.get(`${prefix}/search?q=${qEscaped}${typeQuery}`);
  },
  async getProfile(options) {
    const id = (options && options.member_id) ? options.member_id : "";
    return await axios.get(`${prefix}/player/${id}`);
  },
  async getGames(options) {
    const id = (options && options.member_id) ? options.member_id : "";
    const periodQuery = (options && options.period) ? `?period=${encodeURIComponent(options.period)}` : "";
    return await axios.get(`${prefix}/player/${id}/games${periodQuery}`);
  },
  async searchClubs(options) {
    const qEscaped = encodeURIComponent((options && options.q) ? options.q.trim() : "");
    return await axios.get(`${prefix}/clubs?q=${qEscaped}`);
  },
  async getClubPlayers(options) {
    const clubId = (options && options.club_id) ? options.club_id : "";
    return await axios.get(`${prefix}/club/${clubId}/players`);
  },
  async getAllClubs() {
    return await axios.get(`${prefix}/clubs/all`);
  }
};

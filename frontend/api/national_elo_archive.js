import axios from "axios";

const prefix = "/api/v1/national_elo_archive";
export default {
  search: async function(options) {
    const typeQuery = options.type ? `&type=${options.type}` : "";
    return await axios.get(`${prefix}/search?q=${options.q}${typeQuery}`);
  },
  getProfile: async function(options) {
    return await axios.get(`${prefix}/player/${options.member_id}`);
  },
  getGames: async function(options) {
    const periodQuery = options.period ? `?period=${options.period}` : "";
    return await axios.get(`${prefix}/player/${options.member_id}/games${periodQuery}`);
  },
  searchClubs: async function(options) {
    return await axios.get(`${prefix}/clubs?q=${options.q}`);
  },
  getClubPlayers: async function(options) {
    return await axios.get(`${prefix}/club/${options.club_id}/players`);
  },
  getAllClubs: async function() {
    return await axios.get(`${prefix}/clubs/all`);
  }
};

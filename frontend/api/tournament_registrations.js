import axios from "axios";

const prefix = "/api/v1/tournament_registrations";

export default {
  // ---- public: tournament + lookup + registrations ----

  getTournament: async function (options) {
    const { id } = options;
    return await axios.get(`${prefix}/${id}`);
  },

  lookup: async function (options) {
    const { id, q } = options;
    const qEscaped = encodeURIComponent(q ? q.trim() : "");
    return await axios.get(`${prefix}/${id}/lookup?q=${qEscaped}`);
  },

  // Tournament-independent sibling of lookup() above -- no id in the path,
  // for contexts where there's no tournament id yet (e.g. the arbiter/
  // organizer picker while creating a brand new tournament).
  lookupGlobal: async function (options) {
    const { q } = options;
    const qEscaped = encodeURIComponent(q ? q.trim() : "");
    return await axios.get(`${prefix}/lookup?q=${qEscaped}`);
  },

  // Public, field-restricted (no date_birth/email/phone/gsm/submitted_ip --
  // see PUBLIC_REGISTRATION_COLUMNS server-side). Use admin_getRegistrations
  // for the full-fidelity admin view.
  getRegistrations: async function (options) {
    const { id } = options;
    return await axios.get(`${prefix}/${id}/registrations`);
  },

  // Full-fidelity, public, no auth beyond knowing the row's own id -- same
  // trust model as updateRegistration below. Used to prefill the edit-own-
  // registration dialog, which needs real date_birth etc.; the public LIST
  // response above no longer carries that.
  getRegistration: async function (options) {
    const { id } = options;
    return await axios.get(`${prefix}/registrations/${id}`);
  },

  // Full-fidelity sibling of getRegistrations, for the admin dashboard.
  admin_getRegistrations: async function (options) {
    const { id, token } = options;
    return await axios.get(`${prefix}/admin/tournaments/${id}/registrations`, {
      headers: { Authorization: "Bearer " + token },
    });
  },

  createRegistration: async function (options) {
    const { id, ...registration } = options;
    return await axios.post(`${prefix}/${id}/registrations`, registration);
  },

  // Public edit-by-id: matches the legacy tool (no per-registrant auth,
  // just knowledge of the registration's own id) -- deliberately no token.
  updateRegistration: async function (options) {
    const { id, ...registration } = options;
    return await axios.put(`${prefix}/registrations/${id}`, registration);
  },

  // ---- admin (Authorization: Bearer <tournament_registrations JWT>) ----

  admin_login: async function (options) {
    const { username, password } = options;
    return await axios.post(`${prefix}/admin/login`, { username, password });
  },

  admin_getMyTournaments: async function (options) {
    const { token } = options;
    return await axios.get(`${prefix}/admin/tournaments/mine`, {
      headers: { Authorization: "Bearer " + token },
    });
  },

  admin_createTournament: async function (options) {
    const { token, ...tournament } = options;
    return await axios.post(`${prefix}/admin/tournaments`, tournament, {
      headers: { Authorization: "Bearer " + token },
    });
  },

  admin_updateTournament: async function (options) {
    const { id, token, ...tournament } = options;
    return await axios.put(`${prefix}/admin/tournaments/${id}`, tournament, {
      headers: { Authorization: "Bearer " + token },
    });
  },

  admin_deleteTournament: async function (options) {
    const { id, token } = options;
    return await axios.delete(`${prefix}/admin/tournaments/${id}`, {
      headers: { Authorization: "Bearer " + token },
    });
  },

  admin_updateRegistration: async function (options) {
    const { id, token, ...registration } = options;
    return await axios.put(`${prefix}/admin/registrations/${id}`, registration, {
      headers: { Authorization: "Bearer " + token },
    });
  },

  admin_deleteRegistration: async function (options) {
    const { id, token } = options;
    return await axios.delete(`${prefix}/admin/registrations/${id}`, {
      headers: { Authorization: "Bearer " + token },
    });
  },

  // CSV/SWAR exports return a raw file, not JSON -- responseType "blob" so
  // axios doesn't try to parse it, and the page turns the blob into a
  // download via an object URL. Note: on an error response (e.g. scoped 403)
  // axios still applies responseType "blob" to the error body, so the usual
  // error.response.data.detail extraction in plugins/backend.js can't read
  // it and falls back to the generic status-code message -- acceptable for
  // these two rarely-failing, admin-only download actions.
  admin_exportCsv: async function (options) {
    const { id, token } = options;
    return await axios.get(`${prefix}/admin/tournaments/${id}/export/csv`, {
      headers: { Authorization: "Bearer " + token },
      responseType: "blob",
    });
  },

  admin_exportSwar: async function (options) {
    const { id, category, token } = options;
    return await axios.get(
      `${prefix}/admin/tournaments/${id}/export/swar/${category}`,
      {
        headers: { Authorization: "Bearer " + token },
        responseType: "blob",
      }
    );
  },

  admin_refreshElo: async function (options) {
    const { id, token } = options;
    return await axios.post(
      `${prefix}/admin/tournaments/${id}/refresh-elo`,
      {},
      {
        headers: { Authorization: "Bearer " + token },
      }
    );
  },
};

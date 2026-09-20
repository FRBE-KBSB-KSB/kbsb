import axios from "axios";

const prefix1 = "/api/v1/accounts";   // google account in reddevil/account
const prefix2 = "/api/v1/member";     // odoo account in member
export default {
  googlelogin: async function(options) {
    return await axios.post(`${prefix1}/anon/login`, options);
  },
  odoologin: async function(options) {
    return await axios.post(`${prefix2}/login`, options);
  },
};

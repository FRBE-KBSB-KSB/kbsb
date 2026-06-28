import axios from "axios";

const prefix = "/api/v1/fide";
export default {
  formdata: async function() { 
    return await axios.get(`${prefix}/form-data`);
  },
  generate: async function(options){
    const { locale, ...formdata} = options
    return await axios.post(
      `${prefix}/generate?locale=${locale}`, 
      formdata, 
      { responseType: "blob"}
    )
  },
};

import axios from "axios";

const prefix = "/api/test";
export default {
    excel: async function() { 
        const response = await axios.get(`${prefix}/excel`, 
            {
                responseType: 'blob'
            } // CRITICAL: Tells Axios to treat response data as a binary Blob
        );
        console.log("api file", response)
        return response
    },
};

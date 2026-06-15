import axios from "axios";

const prefix = "/api/v1/fide";
export default {
  formdata: async function() {
    return await axios.get(`${prefix}/form-data`);
  },
  generate: async function(options){
    const { locale, ...formdata} = options
    return await axios.post(`${prefix}/generate?locale=${locale}`, formdata)
  },
};

// async function downloadExcel() {
//     const requestBody = {
//         filename: "monthly_sales_2026",
//         report_title: "Sales Data",
//         data: [
//             { "ID": 1, "Item": "Mechanical Keyboard", "Price": 99.99, "Stock": 45 },
//             { "ID": 2, "Item": "Wireless Mouse", "Price": 49.99, "Stock": 120 },
//             { "ID": 3, "Item": "UltraWide Monitor", "Price": 399.99, "Stock": 15 }
//         ]
//     };

//     try {
//         // Make the POST request with Axios
//         const response = await axios.post("http://127.0.0.1:8000/api/export-excel", requestBody, {
//             responseType: 'blob' // CRITICAL: Tells Axios to treat response data as a binary Blob
//         });

//         // Axios stores the binary blob directly in response.data
//         const blob = response.data;

//         // Create a local temporary URL for the blob
//         const downloadUrl = window.URL.createObjectURL(blob);

//         // Programmatically create an anchor element to trigger the download
//         const link = document.createElement("a");
//         link.href = downloadUrl;
        
//         // Use the filename provided in the request payload
//         link.download = `${requestBody.filename}.xlsx`;
        
//         // Append, trigger click, and cleanup
//         document.body.appendChild(link);
//         link.click();
        
//         document.body.removeChild(link);
//         window.URL.revokeObjectURL(downloadUrl);

//     } catch (error) {
//         console.error("Error downloading the Excel file:", error);
//     }
// }
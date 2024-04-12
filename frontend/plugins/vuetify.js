import "@mdi/font/css/materialdesignicons.css"
import "vuetify/styles"
import { createVuetify } from "vuetify"

export default defineNuxtPlugin((app) => {
  const vuetify = createVuetify({})
  app.vueApp.use(vuetify)
})


// import { createVuetify } from "vuetify";
// import * as directives from "vuetify/directives";
// import "vuetify/styles";

// export default defineNuxtPlugin((nuxtApp) => {
//   const vuetify = createVuetify({
//     ssr: true,
//     directives,
//   });

//   nuxtApp.vueApp.use(vuetify);
// });
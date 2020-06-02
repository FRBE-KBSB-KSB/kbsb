import Vue from 'vue'
import vuetify from '@/plugins/vuetify';

// window.config must be configured before the store is loaded
// now fake the server side injection in landingpage.html in a dev environment

import Page from './Page.vue'
// import './registerServiceWorker'
import {router} from './router_page'
import store from './store_page'

Vue.config.productionTip = false

window.vm = new Vue({
  vuetify,
  router,
  store,
  render: h => h(Page)
}).$mount('#app')


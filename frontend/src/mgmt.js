import Vue from 'vue'
import VueRouter from 'vue-router'
import store from './store/mgmt'
import { i18n } from './util/lang'
import './util/vuetify'

import Mgmt from './pages/Mgmt'
import MgmtArticles from './pages/MgmtArticles'
import MgmtDocuments from './pages/MgmtDocuments'
import MgmtMembers from './pages/MgmtMembers'

Vue.config.productionTip = false;

Vue.use(VueRouter);

const router = new VueRouter({
  routes: [
    {path: '/articles', component: MgmtArticles},
    {path: '/documents', component: MgmtDocuments},
    {path: '/members', component: MgmtMembers},
    {path: '*', redirect: '/articles'},
  ],
  mode: 'hash',
});


window.application = {
  Vue: Vue,
  App: Mgmt,
  store: store,
  i18n: i18n,
  router,
};

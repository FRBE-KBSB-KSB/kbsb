import Vue from 'vue'
import VueRouter from 'vue-router'
import store from './store/mgmt'
import { i18n } from './util/lang'
import './util/vuetify'

import ViewArticle from './pages/ViewArticle'

Vue.config.productionTip = false;

Vue.use(VueRouter);

window.application = {
  Vue: Vue,
  App: ViewArticle,
  store: store,
  i18n: i18n
};

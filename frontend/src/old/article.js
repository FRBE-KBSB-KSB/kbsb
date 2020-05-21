import Vue from 'vue'
import { i18n } from './util/lang'
import VueRouter from 'vue-router'
import store from './store/mgmt'
import marked from 'marked'
import './util/vuetify'

import ViewArticle from './pages/ViewArticle'

window.config.marked = marked;

Vue.config.productionTip = false;

Vue.use(VueRouter);

window.application = {
  Vue: Vue,
  App: ViewArticle,
  store: store,
  i18n: i18n
};

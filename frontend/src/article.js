import Vue from 'vue'
import VueRouter from 'vue-router'
import store from './store/mgmt'
import marked from 'marked'
import { i18n } from './util/lang'
import './util/vuetify'

import ViewArticle from './pages/ViewArticle'

window.config = window.config || {};
window.config.marked = marked;

console.log('window.config in article.js 2', window.config);

Vue.config.productionTip = false;

Vue.use(VueRouter);

window.application = {
  Vue: Vue,
  App: ViewArticle,
  store: store,
  i18n: i18n
};

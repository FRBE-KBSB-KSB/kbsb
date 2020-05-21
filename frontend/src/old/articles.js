import Vue from 'vue'
import VueRouter from 'vue-router'
import store from './store/mgmt'
import marked from 'marked'

import { i18n } from './util/lang'
import './util/vuetify'

import ViewArticles from './pages/ViewArticles'

window.config = {marked: marked};
console.log('window.config in cms.js 2', window.config);

Vue.config.productionTip = false;

Vue.use(VueRouter);


window.application = {
  Vue: Vue,
  App: ViewArticles,
  store: store,
  i18n: i18n
};

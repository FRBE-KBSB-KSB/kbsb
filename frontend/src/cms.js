import Vue from 'vue'
import { i18n } from './util/lang'
import store from './store'
import marked from 'marked'
import VueCmsPatch from './vue-djangocms-patch'
import './util/vuetify'
import './style/kbsb.styl'

window.config = {marked: marked};
console.log('window.config in cms.js 1', window.config);

import Cms from './pages/Cms.vue'

Vue.config.productionTip = false;

window.application = {
  Vue: Vue,
  App: Cms,
  store: store,
  i18n: i18n,
  VueCmsPatch: VueCmsPatch,
};


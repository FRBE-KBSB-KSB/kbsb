import Vue from 'vue'
import { i18n } from './util/lang'
import VueCmsPatch from './vue-djangocms-patch';
import './util/vuetify'
import './style/kbsb.styl'

import Cms from './pages/Cms.vue'

Vue.config.productionTip = false;

window.application = {
  Vue: Vue,
  App: Cms,
  i18n: i18n,
  VueCmsPatch: VueCmsPatch,
};


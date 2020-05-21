import Vue from 'vue'
import VueI18n from 'vue-i18n'

Vue.use(VueI18n);

let messages = {}
messages[window.config.lang] = window.config.localemsg;

export const i18n = new VueI18n({
  locale: window.config.lang , // set locale
  fallbackLocale: 'en',
  messages,  // set locale messages
})

import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

import { languages } from '@/util/cms'
import { setLanguage } from '@/util/lang'

// setup the locale and the slug
let pparts = window.location.pathname.split('/');
let slug =  pparts.length > 2 ? pparts[2] : 'home';
let locale = pparts.length > 3 ? pparts[3] : window.localStorage.getItem('locale');
locale = locale || navigator.language.split('-')[0]; 
if (! languages.includes(locale)) locale = 'en';

const store = new Vuex.Store({
  state: {
    api: null,
    drawer: false,
    locale: locale,
    slug: slug,
  },

  mutations: {

    updateApi(state, payload) {
      state.api = payload;
    },

    updateDrawer (state, payload) {
      console.log('update drawer', payload)
      state.drawer = payload;
    },

    updateLocale (state, payload) {
      state.locale = payload || state.locale;
      window.localStorage.setItem('locale', state.locale);
      setLanguage(state.locale);
    },

    updateSlug (state, payload) {
      state.slug = payload || state.slug;
    },

  }
})

export default store
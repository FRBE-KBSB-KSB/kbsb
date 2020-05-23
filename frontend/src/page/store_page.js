import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);


// setup the locale and the slug
let supportedLocales = ['en', 'fr', 'de', 'nl'];
let pparts = window.location.pathname.split('/');
let slug =  pparts.length > 2 ? pparts[2] : 'home';
let locale = pparts.length > 3 ? pparts[3] : window.localStorage.getItem('locale');
locale = locale || navigator.language.split('-')[0]; 
if (! supportedLocales.includes(locale)) locale = 'en';

const store = new Vuex.Store({
  state: {
    api: null,
    drawer: false,
    locale: locale,
    slug: slug,
    vuetemplate: 'CmsSimpleTemplate'  
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
      // setLanguage(state.locale);
    },

    updateSlug (state, payload) {
      state.slug = payload || state.slug;
    },

    updateVuetemplate (state, payload) {
      state.vuetemplate = payload;
    },

  }
})

export default store
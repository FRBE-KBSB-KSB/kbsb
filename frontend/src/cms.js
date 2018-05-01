import 'babel-polyfill';
import Vue from 'vue';
import Vuetify from 'vuetify';
import VueLayout from './components/VueLayout';
import VueCmsPatch from './vue-djangocms-patch';
import './stylus/kbsb.styl';

Vue.config.ignoredElements = [
  'cms-template',
  'cms-plugin',
];

Vue.use(Vuetify);

Vue.component('cms-page', {
  components: {
    'vue-layout': VueLayout
  },
  data () {
    return {
      showTranslated: '',
    }
  },
  methods: {
    openTranslation (lang) {
      this.showTranslated = lang;
    }

  },
});

new Vue({
  el: '#app',
  created () {
    new VueCmsPatch(this)
  },
});


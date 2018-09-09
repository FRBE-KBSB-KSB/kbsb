import 'babel-polyfill';
import Vue from 'vue';
import Vuetify from 'vuetify';
import VueLayout from './components/VueLayout';
import AdminMember from './components/AdminMember';
import './stylus/kbsb.styl'

Vue.use(Vuetify);

new Vue({
  el: '#app',
  data () {
    return {
      drawer: false,
    }
  },
  components: {
    'vue-layout': VueLayout,
    'admin-member': AdminMember,
  },
});



import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    drawer: false,
  },
  mutations: {

    // drawer
    updateDrawer(state, value) {
      state.drawer = value;
    },

  }
});

export default store



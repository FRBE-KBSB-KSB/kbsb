import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

const store = new Vuex.Store({

  state: {
    drawer: false,
    article: {},
  },

  mutations: {

    // drawer
    updateDrawer(state, value) {
      state.drawer = value;
    },

    // article
    updateArticle(state, value) {
      state.artcile = value;
    },

  }
});

export default store



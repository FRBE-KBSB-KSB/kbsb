import Vue from 'vue'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'
import colors from 'vuetify/es5/util/colors'

Vue.use(Vuetify, {
    theme: {
        primary: colors.green,
        secondary: colors.green.darken2,
        accent: colors.green.accent2,       
    }
});

export default Vuetify

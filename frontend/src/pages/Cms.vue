<template>
  <v-app>
    <sidebar />
    <topbar />
    <v-parallax  v-if="landing && $vuetify.breakpoint.mdAndUp"
                 src="/static/img/landing_big.jpg" height="400" />
    <v-parallax v-if="landing && $vuetify.breakpoint.sm"
                src="/static/img/landing_medium.jpg" height="300" />
    <v-parallax v-if="landing && $vuetify.breakpoint.xs"
                src="/static/img/landing_small.jpg" height="200" />
    <v-content :class="{landing: landing}">
      <v-container>
        <div class="mainarea my-1">
          <cms-content class="pa-1" />
        </div>
      </v-container>
      <v-parallax  v-if="landing && $vuetify.breakpoint.mdAndUp"
                   src="/static/img/chesscrowd_big.jpg" height="400" />
      <v-parallax  v-if="landing && $vuetify.breakpoint.sm"
                   src="/static/img/chesscrowd_medium.jpg" height="300" />
      <v-parallax v-if="landing && $vuetify.breakpoint.xs"
                  src="/static/img/chesscrowd_small.jpg" height="200" />

    </v-content>

    <ad-carousel class="mt-4 mb-3"/>
    <kbsb-footer />
  </v-app>
</template>

<script>

import { loadLanguageAsync } from '../util/lang'
import marked from 'marked' 

import Sidebar from '../components/Sidebar'
import Topbar from '../components/Topbar'
import KbsbFooter from '../components/KbsbFooter'
import AdCarousel from '../components/AdCarousel'

export default {

  name: 'Cms',

  data () {return {
    tabactive: 0,
    landing: window.config.landing,
    sidebar: window.config.sidebar,

  }},

  components: {
    'sidebar': Sidebar,
    'topbar': Topbar,
    'kbsb-footer': KbsbFooter,
    'ad-carousel': AdCarousel,
  },

  created () {
    loadLanguageAsync(window.config.lang);
  },

}
</script>

<style>
.landing.v-content {
  padding-top: 0px !important;
}
.img-responsive {
  max-width: 100%;
}
</style>
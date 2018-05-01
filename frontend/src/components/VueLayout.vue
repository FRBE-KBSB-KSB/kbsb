<!--
  vue based layout containing 3 slot definitions:
  - 'menu' for the cms menu
  - 'landing-box' for the landing box code
  - unnamed for the cms content
-->

<template>
  <v-app>

    <v-navigation-drawer v-cloak dark temporary fixed v-model="drawer"
                         class="navmax green darken-1">
      <v-toolbar flat class="green">
        <v-list>
          <v-list-tile>
            <v-list-tile-title class="title">
              Menu
            </v-list-tile-title>
          </v-list-tile>
        </v-list>
      </v-toolbar>
      <v-divider></v-divider>
      <div class="btn-language green darken-1">
        <slot name="language-selector"></slot>
      </div>
      <v-list dark dense class="green darken-1">
        <slot name="menu"></slot>
        <v-list-tile  href="/old/interclub.php">
          <v-list-tile-content>
            <v-list-tile-title>Interclub
            </v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>          
        <v-list-tile  href="/news/">
          <v-list-tile-content>
            <v-list-tile-title  v-text="_t['News']"></v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
      </v-list>
      <v-list dark dense class="green darken-1" v-if="authenticated">
        <v-list-group>
        <v-list-tile slot="activator" @click="">
            <v-list-tile-content>Admin</v-list-tile-content>
        </v-list-tile>
        <v-list-tile href="/mgmt/">
            <v-list-tile-action></v-list-tile-action>
            <v-list-tile-content>
            <v-list-tile-title v-text="_t['News']"></v-list-tile-title>
            </v-list-tile-content>
        </v-list-tile>
        </v-list-group>
      </v-list>
    </v-navigation-drawer>

    <v-toolbar v-cloak fixed dark app :class="toolbar_classes"
               class="green darken-2" >
      <v-toolbar-side-icon @click.stop="drawer = !drawer"></v-toolbar-side-icon>
      <v-toolbar-items>
        <v-btn flat large href="/" v-text="_t['RBCF']"></v-btn>
      </v-toolbar-items>
      <v-spacer></v-spacer>
      <v-toolbar-items class="hidden-sm-and-down">
        <v-btn flat large href="/old/interclub">
          Interclub
        </v-btn>
        <v-btn flat large href="/news/">
          <span  v-text="_t['News']"></span>
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>

    <slot name="landing-box"></slot>

    <v-content>
      <v-container>
        <slot></slot>
        <slot name="translated"></slot>
      </v-container>
    </v-content>

    <v-footer height="auto" >
      <v-layout column>
        <v-flex class="mt-2">
          <ad-carousel/>
        </v-flex>
        <v-flex>
          <v-container fluid class="green darken-1">
            <v-layout row wrap class="py-2 footer green darken-1  white--text">
              <v-flex md3 sm6 xs12 class="pl-2">
                <a href="/bycco/us" v-text="_t['About RBCF']"></a>
              </v-flex>
              <v-flex md3 sm6 xs12 class="pl-2">
                <a href="/bycco/team" v-text="_t['The team']"></a>
              </v-flex>
              <v-flex md3 sm6 xs12 class="pl-2">
                <span v-text="_t['Contact']"></span>
                <a href="mailto:board@frbe-kbsb.be">board@frbe-kbsb.be</a>
              </v-flex>
              <v-flex md3 sm6 xs12 class="pl-2">
                <a href="https://www.facebook.com/groups/1845828638985199">
                <img src="/static/img/facebook.png">
                </a>
              </v-flex>
            </v-layout>
          </v-container>

        </v-flex>
      </v-layout>
    </v-footer>

  </v-app>
   
</template>

<script>

import AdCarousel from './AdCarousel';
import _ from 'lodash';

export default {

  data () {
    return {
      drawer: false,
      lang: window.config.lang,
      authenticated: window.config.authenticated,
      toolbar_classes: [window.config.toolbar_class],
      _t: {},
    }
  },
  components: {
    "ad-carousel": AdCarousel,
  },
  methods: {
    gotoUrl (url) {
      console.log('going to ', url)
    },
    clickedMenu (item) {
        console.log('clicked menu', item)
    },
  },
  mounted() {
    var self = this;
    _.forEach(window._t, function (v, k) {
      self._t[k] = v;
    });
    if (window.CMS) {
      console.log('fixing top for CMS toolbar');
      this.toolbar_classes.push('fix-toolbar');
    };
  },
}


</script>

<style scoped>

</style>

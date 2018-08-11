<!--

   Copyright 2017 - 2018 Chessdevil Consulting BVBA

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

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
      <div class="green darken-1">
        <v-btn flat :href="urlI18n('nl')" class="btn-language">NL</v-btn>
        <v-btn flat :href="urlI18n('fr')" class="btn-language">FR</v-btn>
        <v-btn flat :href="urlI18n('de')" class="btn-language">DE</v-btn>
        <v-btn flat :href="urlI18n('en')" class="btn-language">EN</v-btn>
      </div>
      <v-list dark dense class="green darken-1">
        <slot name="menu"></slot>
      </v-list>
      <v-list dark dense class="green darken-1" v-if="authenticated">
        <v-list-group>
          <v-list-tile slot="activator" @click="">
              <v-list-tile-content>Admin</v-list-tile-content>
          </v-list-tile>
        </v-list-group>
      </v-list>
    </v-navigation-drawer>

    <v-toolbar v-cloak fixed dark app class="green darken-2"
               :class="{fixtoolbar: fixtoolbar}">
      <v-toolbar-side-icon @click.stop="drawer = !drawer"></v-toolbar-side-icon>
      <v-toolbar-items>
        <v-btn flat large href="/">{{ _t['RBCF'] }}</v-btn>
      </v-toolbar-items>
      <v-spacer></v-spacer>
      <v-toolbar-items class="hidden-sm-and-down">
        <v-btn flat large :href="oldInterclub()">
          Interclub
        </v-btn>
        <v-btn flat large href="/news/">
          <span  v-text="_t['News']"></span>
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>


    <slot name="landing-box"></slot>

    <slot></slot>

    <slot v-cloak name="translated"></slot>

    <v-footer height="auto" >
      <v-layout column>
        <v-flex class="mt-2">
          <ad-carousel/>
        </v-flex>
        <v-flex>
          <v-container fluid class="green darken-1">
            <v-layout row wrap class="py-2 footer green darken-1  white--text">
              <v-flex md3 sm6 xs12 class="pl-2">
                <a href="/about">{{ _t['About RBCF'] }}</a>
              </v-flex>
              <v-flex md3 sm6 xs12 class="pl-2">
                <a href="/team">{{ _t['The team'] }}</a>
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
      lang: window.config.lang,
      drawer: false,
      authenticated: window.config.authenticated,
      fixtoolbar: false,
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
    oldInterclub () {
      return window.config.oldsite + '/index.php/interclubs/2018-2019'
    },
    urlI18n (lang) {
      return window.config.urli18[lang];
    }
  },
  mounted() {
    var self = this;
    _.forEach(window._t, function (v, k) {
      self._t[k] = v;
    });
    if (window.CMS) {
      console.log('fixing top for CMS toolbar');
      this.fixtoolbar = true;
    };
  },
}

</script>

<style scoped>

</style>

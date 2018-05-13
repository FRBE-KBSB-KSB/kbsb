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

    <slot name="toptoolbar"></slot>

    <slot name="landing-box"></slot>

    <v-content>
      <slot></slot>
      <slot name="translated"></slot>
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

  props: ['drawer'],
  data () {
    return {
      lang: window.config.lang,
      authenticated: window.config.authenticated,
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
  },
}

</script>

<style scoped>

</style>

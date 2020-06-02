<template>

<v-app>

  <sidebar />
  <topbar />
  
  <v-content>
    <v-container v-show="!routingtableloaded">
      Just a moment. <v-progress-circular indeterminate />
    </v-container>
    <router-view  v-if='routingtableloaded' :key="$route.fullPath" />
  </v-content>

  <kbsb-footer />

  <v-snackbar v-model="snackbar" :color="color" bottom>
    {{ snacktext }}
    <v-btn text @click="snackbar = false">
      <v-icon>cancel</v-icon>
    </v-btn>
  </v-snackbar>

</v-app>

</template>

<script>
import Swagger from 'swagger-client'
import Sidebar from '@/components/Sidebar.vue'
import Topbar from '@/components/Topbar.vue'
import KbsbFooter from '@/components/KbsbFooter.vue'

import { mapState } from 'vuex'
import { processRoutes } from './router_page'

export default {

  name: 'Default',

  components: {
    Sidebar,
    Topbar,
    KbsbFooter,
  },

  computed: {
    ...mapState(['token', 'api', 'slug', 'locale'])
  },

  data (){return {
    apiloaded: false,
    color: '',
    routingtableloaded: false,
    snackbar: false,
    snacktext: '',    
  }},

  methods: {

    getOpenApi() {
      let self = this;
      Swagger('/openapi.json').then(
        function(client){
          self.apiloaded = true;
          self.$store.commit('updateApi', client.apis.default)
          self.getRoutingTable()
        },
        function(data){
          console.error('could not fetch openapi.json', data)
          alert('Cannot load API');
        }
      );
    },
    
    getRoutingTable() {
      let self=this;
      let rt;
      this.api.get_routingtable().then(
        function(data){
          self.routingtableloaded = true;
          console.log('got Routes', data.obj.routes)
          rt = processRoutes(data.obj.routes)
          self.$router.addRoutes(rt);
          console.log('rt added', rt, 'going to', self.slug, self.locale)
          // double replace because of vue router bug
          self.$router.replace('/dummy')
          self.$router.replace('/page/' + self.slug + '/' + self.locale)
        },
        function(data){
          console.error('could not fetch routingtable', data).
          alert('Cannot load API');
        }
      )
    },

  },


  mounted() {
    let self=this;
    this.getOpenApi();
    this.$root.$on('snackbar', function(ev) {
      if (ev.text) {
        self.snacktext = ev.text;
        self.snackbar = true;
      }
      if (ev.color) {
        self.color = ev.color;
      }
    });
    this.$router.beforeEach(function(to, from, next){
      let pparts = to.path.split('/');
      if (pparts.length == 4) {
        if (pparts[2] != self.slug) {
          self.$store.commit('updateSlug', pparts[2]);
        }
        if (pparts[3] != self.locale) {
          self.$store.commit('updateLocale', pparts[3]);
        }
      }
      next();
    })
  },


}
</script>


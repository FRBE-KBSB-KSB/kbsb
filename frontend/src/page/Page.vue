<template>

<v-app>

  <sidebar />
  <topbar />
  
  <v-main>
    <v-container v-show="!routingtableloaded">
      Just a moment. <v-progress-circular indeterminate />
    </v-container>
    <router-view  v-if='routingtableloaded' :key="$route.fullPath" />
  </v-main>

  <ad-carousel />

  <kbsb-footer />

  <v-snackbar v-model="snackbar" top>
    {{ snacktext }} 
    <template v-slot:action="{ attrs }">
      <v-btn text v-bind="attrs" @click="snackbar = false">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </template>
  </v-snackbar>

</v-app>

</template>

<script>
import Swagger from 'swagger-client'
import Sidebar from '@/components/Sidebar.vue'
import Topbar from '@/components/Topbar.vue'
import AdCarousel from '@/components/AdCarousel.vue'
import KbsbFooter from '@/components/KbsbFooter.vue'
import { setLanguage } from '@/util/lang'


import { mapState } from 'vuex'
import { processRoutes } from './router_page'

export default {

  name: 'Default',

  components: {
    Sidebar,
    Topbar,
    KbsbFooter,
    AdCarousel,
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
      this.api.anon_routingtable().then(
        function(data){
          self.routingtableloaded = true;
          console.log('got Routes', data.obj.routes)
          rt = processRoutes(data.obj.routes)
          self.$router.addRoutes(rt);
          // double replace because of vue router bug
          let newroute = '/page/' + self.slug + '/' + self.locale;
          if (self.$route.path == newroute) {
            self.$router.replace('/dummy')
          }
          self.$router.replace(newroute)
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
    setLanguage(this.locale)     
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


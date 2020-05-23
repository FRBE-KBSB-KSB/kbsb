json <template>

<v-app>

  <sidebar />
  <topbar  :cuetemplate="vuetemplate" />
  
  <v-content>
    <v-container v-show="!routingtableloaded">
      Just a moment, loading ...
    </v-container>
    <router-view  v-if='routingtableloaded'  
                  :key="$route.fullPath" />
  </v-content>

  <kbsb-footer />

</v-app>

</template>

<script>
import Swagger from 'swagger-client'
import Sidebar from '@/components/Sidebar.vue'
import Topbar from '@/components/Topbar.vue'
import KbsbFooter from '@/components/KbsbFooter.vue'

import { mapState } from 'vuex'
import { processRoutes } from './router_page'
// import CmsSimplePage from './CmsSimplePage.vue'

export default {

  name: 'Default',

  components: {
    Sidebar,
    Topbar,
    KbsbFooter,
  },

  computed: {
    ...mapState(['token', 'api', 'slug', 'locale', 'vuetemplate'])
  },

  data (){return {
    apiloaded: false,
    routingtableloaded: false
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
          self.$router.push('/page/' + self.slug + '/' + self.locale)
        },
        function(data){
          console.error('could not fetch routingtable', data)
          alert('Cannot load API');
        }
      )
    },

  },


  mounted() {
    this.getOpenApi()
  }

}
</script>

<style scoped>

</style>

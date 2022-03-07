<template>

  <v-container class="mt-1 markedcontent">
  <v-tabs light slider-color="deep-purple" v-model="lang" >
    <v-tab class="mx-2"  v-for="l in p.languages" :key="l">
      <span>{{l}}</span>
    </v-tab>
  </v-tabs>
  <v-tabs-items v-model="lang">
    <v-tab-item  v-for="l in p.languages" :key="l">
      <div class='elevation-1 mt-2 pa-2'>
        <h1 v-html="p.title[l].value" />
        <div v-html="marked(p.intro[l].value)" class="mt-1"/>
        <hr/>
        <div v-html="marked(p.body[l].value)" class="mt-1" />
      </div>
    </v-tab-item>
  </v-tabs-items>      

  </v-container>

</template>

<script>
import {mapState} from "vuex"
import marked from 'marked'

export default {

  name: 'MultiLocalePage',

  data () {return {
    p: {},
    lang: '',
  }},

  computed: {

    ...mapState(['api', 'locale', 'slug']),

  },

  methods: {
    
    getContent () {
      let self=this;
      this.api.anon_slug_page({
        slug: this.slug,
      }).then(
        function(data){
          self.p =  data.obj;
        },
        function(data){
          console.error('could not fetch localized page', data)
        }
      )
    },

    marked(s) {
      return marked(s)
    },

  },

  mounted () {
    this.getContent();
  },


}
</script>


<style scoped>

.markedcontent table {
  border-collapse: collapse;
  min-width: 30em;
}

.markedcontent table {
  border: 1px solid black;
}

.markedcontent td {
  border: 1px solid black;
  padding: 6px;
}

.markedcontent  th {
  border: 1px solid black;
  padding: 6px;
}

</style>

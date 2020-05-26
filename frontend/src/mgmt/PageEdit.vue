<template>
<v-container class="elevation-1">
  <v-row>
    <v-col cols=12 sm=6>
        <h1>Edit Page: {{ name }} </h1>
    </v-col>
    <v-col col=12 sm=6>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" outlined fab color="deep-purple" @click="back()" 
              slot="activator">
            <v-icon>mdi-arrow-left</v-icon>
          </v-btn>
        </template>
        <span>Go Back</span>
      </v-tooltip>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" outlined fab color="deep-purple" @click="save()" 
              slot="activator">
            <v-icon>mdi-content-save</v-icon>
          </v-btn>
        </template>
        <span>Save page</span>
      </v-tooltip>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" outlined fab color="deep-purple" @click="remove()" 
              slot="activator">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
        <span>Delete page</span>
      </v-tooltip>

      <!-- <v-tooltip bottom >
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" outlined fab color="deep-purple" @click="publish()" 
              slot="activator">
            <v-icon>mdi-publish</v-icon>
          </v-btn>
        </template>
        <span>Publish now</span>
      </v-tooltip>
      <v-tooltip bottom >
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" outlined fab color="deep-purple" @click="preview()" 
              slot="activator">
            <v-icon>mdi-eye</v-icon>
          </v-btn>
        </template>
        <span>Preview page</span>
      </v-tooltip> -->
    </v-col>
  </v-row>
  <v-row>
    <v-col cols=12 sm=6>
      <v-text-field label="Name" v-model="p.name" />
      <v-text-field label="Owner" v-model="p.created_by" />
      <v-select :items="pagecomponents" label="Frontend Component" v-model="p.component" />         
    </v-col>
    <v-col cols=12 sm=6>
      <v-row >
        <v-col cols=3 v-for="l in lang.available" :key="l">
          <v-switch v-model="lang.enabled[l]" :label="l" @change="toggleLang(l)" />
        </v-col>
      </v-row>
      <v-text-field label="Slug" v-model="p.slug" />
      <p>Page created: <date-formatted :date="p.created_ts"/></p>
      <p>Page modified: <date-formatted :date="p.modified_ts"/></p>
    </v-col>
  </v-row>
  <v-tabs light slider-color="deep-purple" v-model="lang.current" >
    <v-tab class="mx-2"  v-for="l in enabledLang" :key="l">
      <span>{{l}}</span>
    </v-tab>
  </v-tabs>
  <v-tabs-items v-model="lang.current">
    <v-tab-item  v-for="l in enabledLang" :key="l">
      <div class='elevation-1 mt-2 pa-2'>
        <v-text-field label="Title" v-model="p.page_i18n_fields[l].title" />
        <v-textarea auto-grow rows=3 label="Intro" 
                    v-model="p.page_i18n_fields[l].intro" /> 
        <v-textarea auto-grow rows=8 label="Body" v-model="p.page_i18n_fields[l].body" /> 
      </div>
    </v-tab-item>
  </v-tabs-items>

</v-container>
</template>

<script>

import DateFormatted from "@/components/DateFormatted"
import { mapState } from 'vuex'
import { bearertoken } from "@/util/token"

let pagecomponents = [
  'CmsSimplePage',
  'LandingPage',
]

let languages = ['nl', 'fr', 'de', 'en']

export default {

  name: "PageEdit",

  components: {
    DateFormatted,
  },

  computed: {
    ...mapState(['token', 'api']),
    enabledLang: function(){
      let la = [], self=this;
      this.lang.available.forEach(function(l){
        if (self.lang.enabled[l] === true) {
          la.push(l)
        }
      })
      return la      
    },
  },

  data () {return {
    lang: {
      available: languages,
      current: 0,
      enabled: {},
    },
    name: '', 
    p: {},
    pagecomponents: pagecomponents,
    yesno: [
      {value:true, text: 'Yes'},
      {value:false ,text:'No'}
    ],
  }},

  methods: {

    back () {
      this.$router.push('/mgmt/page/list');
    },

    getPage() {
      let self=this;
      this.api.get_page(
        {id: this.$route.params.id},
        {securities: bearertoken(this.token)},
      ).then(
        function(data) {
          self.readPage(data.obj.page);
        },
        function(data){
          console.error('failed get page', data)
        }
      );
    },

    preview () { },

    publish() { },

    readPage (page) {
      let self=this;
      this.p = page;
      this.p.languages.forEach(function(l){
        if (l in self.p.page_i18n_fields === false) {
          self.p.page_i18n_fields[l] = {
            body: '',
            intro: '',
            title: '',
          };
        }
        self.$set(self.lang.enabled, l, true);
      })
      this.name = this.p.name + '';
    },

    remove () {
      let self=this;
      if (window.confirm('Are you sure to delete page "' + this.name + '"?')) {
        this.api.delete_page({
          id: this.$route.params.id
        }).then(
          function(){
            // TODO show deleted
            console.log('successfully deleted page')
            self.back();
          }, 
          function(data){
            // TODO show error message
            console.error('failed to delete', data);
          }
        );
      }
    },

    save () {
      let self=this;
      const {id, ...page} = this.p;
      console.log('saving', page);
      this.api.update_page({id},{
        requestBody: page,
        securities: bearertoken(this.token),        
      }).then(
        function(){
          // TODO successfully saved
          console.log('successfully saved page')
        },
        function(data){
          // TODO show error message
          console.error('failed to save', data);
          self.back();
        }
      );
    },

    toggleLang(l){
      this.p.languages = this.enabledLang;
      if (l in this.p.page_i18n_fields === false) {
        this.p.page_i18n_fields[l] = {
          body: '',
          intro: '',
          title: '',
        }
      }
    },
  },

  mounted () {
    this.getPage();
  }

}
</script>

<style scoped>
.bordermd {
  border: 1px solid grey;
}
</style>
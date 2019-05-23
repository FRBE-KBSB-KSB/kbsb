<template>
<v-container fluid grid-list-md class="elevation-1">
  <v-layout row wrap>
    <v-flex>
        <h1>Edit Document: {{d.name}} </h1>
    </v-flex>
    <v-flex>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="back()" slot="activator">
          <v-icon>arrow_back</v-icon>
        </v-btn>
        <span>Go Back</span>
      </v-tooltip>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="remove()" slot="activator">
          <v-icon>delete</v-icon>
        </v-btn>
        <span>Delete document</span>
      </v-tooltip>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="save()" slot="activator">
          <v-icon>save</v-icon>
        </v-btn>
        <span>Save changes</span>
      </v-tooltip>
    </v-flex>
  </v-layout>
  <v-layout row wrap>
    <v-flex sm6 xs12>
      <v-select :items="catchoices" label="Category" v-model="d.category" />
      <v-select :items="topicchoices" label="Topic" v-model="d.topic" />
      <v-select :items="doctypechoices" label="Document type" v-model="d.doctype" />
      <v-select :items="localechoices" label="Document language" v-model="d.locale" />
    </v-flex>
    <v-flex sm6 xs12>
      <p>Document uploaded: <date-formatted :date="d.uploaded"/></p>
      <v-menu :close-on-content-click="false" v-model="menu_topicdate"
        :nudge-right="40" lazy transition="scale-transition" offset-y
        full-width min-width="290px">
        <v-text-field slot="activator" v-model="d.topicdate"
          label="Topic date" prepend-icon="event" readonly
        ></v-text-field>
        <v-date-picker v-model="d.topicdate" @input="menu_topicdate = false"
                       color="green" />
      </v-menu>
    </v-flex>
  </v-layout>

</v-container>
</template>

<script>

import api from '../util/api'
import dc from '../util/doctype'
import marked from 'marked'

import DateFormatted from "./DateFormatted"

export default {

  name: "MgmtDocumentEdit",

  components: {
    DateFormatted,
  },

  props: ['document'],


  data () {return {
    catchoices: dc.catchoices,
    d: {},
    doctypechoices: dc.doctypechoices,
    localechoices: dc.localechoices,
    menu_topicdate: false,
    topicchoices: dc.topicchoices,  
  }},

  methods: {

    back () {
      this.$emit('update', {section: 'list'})
    },

    remove () {
      if (window.confirm('Are you sure to delete ' + this.fullname)) {
        api('deleteDocument', {
          id: this.d.id
        }).then(function(){
          this.$emit('update', {section: 'list', params:{}, reload: true,
            text: this.fullname + ' deleted.'})
        }.bind(this), function(data){
          console.error('failed to delete', data);
        })
      }
    },

    save () {
      api('updateDocument', {
        id: this.document.id,
        document: this.p,
      }).then(
        function(){
          this.$emit('update', {section: 'edit' , reload: true,
            text: this.d.name + ' saved.'})
        }.bind(this),
        function(data){
          console.error('failed to save', data);
        }
      );
    },


  },

  mounted () {
    api('getDocument', {
      id: this.document.id
    }).then(
     function(data) {
        this.d = data.document;
        this.d.topicdate = this.d.topicdate ? this.d.topicdate.split(
          ' ')[0]: '';
      }.bind(this)
    )
  }

}
</script>

<style scoped>
</style>
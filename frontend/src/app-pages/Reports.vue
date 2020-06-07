<template>

  <v-container class="mt-1 markedcontent">
    <h1>
      <i18n-text 
        nl="Verslagen" 
        fr="Procès verbaux" 
        de="Berichte" 
        en="Reports" />
    </h1>
    <v-data-table :headers="headers" :items="files" :footer-props="footerProps"
      class="elevation-1" sort-by="fullname">
    <template v-slot:top>
      <v-toolbar flat color="white">
        <v-toolbar-title>
        <i18n-text 
          nl="Verslagen" 
          fr="Procès verbaux" 
          de="Berichte" 
          en="Reports" />          
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-tooltip bottom >
          <template v-slot:activator="{ on }">
            <v-btn v-on="on" @click="addFile()" fab outlined 
                  color="deep-purple">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </template>
          <span>Add File</span>
         </v-tooltip>
      </v-toolbar>
    </template>
    <template v-slot:item.topic="{ item }">
      {{ t_topic(item) }}
    </template>
    <template v-slot:item.topic_ts="{ item }">
      <date-formatted :date="item.topic_ts" fmt="ll" />
    </template>
    <template v-slot:item.path="{ item }">
      URL: <a :href="fileurl +  item.url">{{ item.name}}</a>      
    </template>
    <template v-slot:no-data>
      No reports yet.
    </template>            
  </v-data-table>
  </v-container>

</template>

<script>

import I18nText from "@/components/I18nText"
import {mapState} from "vuex"
import DateFormatted from "@/components/DateFormatted"
import { fileurl, reportlisting, topic_i18n } from '@/util/cms'
import * as moment from 'moment';

export default {

  name: 'Reports',

  components: {
    DateFormatted,
    I18nText,
  },

  data () {return {
    headers: [
      {
        text: '', value: 'name'
      },
      {
        text: '', value: 'topic'
      },
      {
        text: '', value: 'topic_ts'
      },
      {
        text: '', value:"path"
      }
    ],    
    files: [],
    fileurl: fileurl,
    footerProps: {
      itemsPerPageOptions: [20,50,-1],
      itemsPerPage: 20
    },    
  }},

  computed: {
    ...mapState(['locale', 'api']),
  },

  methods: {

    getReports() {
      let self=this;
      this.api.get_files({'reports': 1}).then(
        function(data) {
          self.files = data.obj.files;
        },
        function(data){
          console.error('getting getFiles', data);
          self.$root.$emit('snackbar', {text: 'Getting files failed', reason: data})            
        }
      );
    },

    t_topic(item){
      return topic_i18n[item.topic][this.locale]
    }
    
  },

  mounted () {
    moment.locale(this.locale)
    this.getReports();
    this.headers[0].text = reportlisting[this.locale][0]
    this.headers[1].text = reportlisting[this.locale][1]
    this.headers[2].text = reportlisting[this.locale][2]
    this.headers[3].text = reportlisting[this.locale][3]

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

<template>

  <v-container class="mt-1 markedcontent">
    <h1>
      <i18n-text 
        nl="Verslagen" 
        fr="Procès verbaux" 
        de="Berichte" 
        en="Reports" />
    </h1>
    <v-data-table :headers="headers" :items="filteredfiles" :footer-props="footerProps"
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
        <v-row>
          <v-col cols=6>
            <v-checkbox v-model="filter.board" 
              :label="t_topic['Report Board Meeting']"/>
          </v-col>
          <v-col cols=6>
            <v-checkbox v-model="filter.ga" 
              :label="t_topic['Report General Assembly']"/>
          </v-col>
        </v-row>
      </v-toolbar>
    </template>
    <template v-slot:item.topic="{ item }">
      {{ t_topic[item.topic] }}
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
    filter: {},    
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
    filteredfiles: function() {
      let self=this, fa=[];
      if (!this.filter.board && !this.filter.ga)
        return this.files;
      this.files.forEach(function(f){
        console.log('topic', f.topic)
        if (f.topic == 'Report Board Meeting' && self.filter.board) {
          console.log('pushing board')
          fa.push(f);
          return
        }
        if (f.topic == 'Report General Assembly' && self.filter.ga) {
          fa.push(f);
          return
        }
      })
      return fa
    },
    t_topic () {
      let k = {};
      k['Report Board Meeting'] = topic_i18n['Report Board Meeting'][this.locale]
      k['Report General Assembly'] = topic_i18n['Report General Assembly'][this.locale]
      return k;
    }     
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

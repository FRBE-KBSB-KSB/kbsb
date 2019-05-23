<template>
<v-container fluid grid-list-md class="elevation-1">
  <v-layout row wrap>
    <v-flex>
        <h1>New Document</h1>
    </v-flex>
    <v-flex>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="back()" slot="activator">
          <v-icon>arrow_back</v-icon>
        </v-btn>
        <span>Go Back</span>
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
      <v-menu :close-on-content-click="false" v-model="menu_topicdate"
        :nudge-right="40" lazy transition="scale-transition" offset-y
        full-width min-width="290px">
        <v-text-field slot="activator" v-model="d.topicdate"
          label="Topic date" prepend-icon="event" readonly
        ></v-text-field>
        <v-date-picker v-model="d.topicdate" @input="menu_topicdate = false"
                       color="green" />
      </v-menu>
      <div class="mt-2">
        <h4>Drop Area</h4>
        <file-pond ref="pond" @addfile="handleFile" className="dropbox" /> 
      </div>
      <p>Generated slug: {{ slug }}</p>
    </v-flex>
  </v-layout>

</v-container>
</template>

<script>

import api from '../util/api'
import dc from '../util/doctype'
import DateFormatted from "./DateFormatted";

export default {
  name: "MgmtDocumentAdd",

  components: {
    DateFormatted,
  },

  computed : {
    slug () {
      let parts = [];
      if (this.d.category) parts.push(this.d.category) ;
      if (this.d.topic) parts.push(this.d.topic);
      if (this.d.locale) parts.push(this.d.locale);
      if (this.d.topicdate) parts.push(this.d.topicdate);
      if (parts.length == 4 && this.d.doctype)
        return parts.join('__') + '.' + this.d.doctype;
      return ''

    }
  },

  data () {return {
    d: {},
    catchoices: dc.catchoices,
    doctypechoices: dc.doctypechoices,
    filecontent: null,
    localechoices: dc.localechoices,
    menu_topicdate: false,
    reading: false,
    topicchoices: dc.topicchoices,
  }},

  methods: {

    back () {
      this.$emit('update', {section: 'list', params:{}})
    },

    handleFile(err, file){
      const reader = new FileReader();
      this.reading = true;
      this.d.name = file.filename;
      reader.onload = (event) => {
        this.filecontent = event.target.result;
        this.reading = false;
      };
      reader.readAsDataURL(file.file);
    },

    save () {
      let doc = this.d;
      doc.slug = this.slug;
      doc.filecontent = this.filecontent;
      api('addDocument', {
        document: doc,
      }).then(
        function(){
          this.$emit('update', {
            section: 'list', 
            reload: true,
            text: 'document uploaded.'
          })
        }.bind(this),
        function(data){
          console.error('failed to save', data);
        }
      );
    },
  },


}
</script>

<style scoped>

</style>
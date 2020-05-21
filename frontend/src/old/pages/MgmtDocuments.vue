<template>
<v-container fluid>

  <mgmt-document-list @update="update($event)" v-show="section == 'list'" 
    :selection="selection"  :ts="ts" />
  <mgmt-document-edit @update="update($event)" v-if="section == 'edit'"
    :document="document" :ts="ts"/>
  <mgmt-document-add @update="update($event)" v-if="section == 'add'"/>

  <v-snackbar v-model="snackbar" :timeout="timeout" bottom>
    {{ snacktext }}
    <v-btn flat @click="snackbar = false">
      <v-icon>cancel</v-icon>
    </v-btn>
  </v-snackbar>

</v-container>
</template>

<script>

import MgmtDocumentList from '../components/MgmtDocumentList'
import MgmtDocumentEdit from '../components/MgmtDocumentEdit'
import MgmtDocumentAdd from '../components/MgmtDocumentAdd'

export default {

  name: "MgmtDocuments",

  data () {return {
    section: 'list',
    selection: [],
    snackbar: false,
    snacktext: '',
    document: {},
    ts: new Date(),
    timeout: 4000,
  }},

  components: {
    MgmtDocumentList,
    MgmtDocumentEdit,
    MgmtDocumentAdd,
  },

  methods: {
    update (e) {
      console.log('update', e);
      if (e.section)
        this.section = e.section;
      if (e.document)
        this.document = e.document;
      if (e.reload) 
        this.ts = new Date();
      if (e.text) {
        this.snacktext = e.text;
        this.snackbar = true;
      }
    }
  }
}
</script>

<style scoped>

</style>
<template>
<v-container fluid grid-list-md class="elevation-1">
  <v-layout row>
    <v-flex>
        <h1>Management Documents</h1>
    </v-flex>
    <v-flex>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="gotoAdd" slot="activator">
          <v-icon>add</v-icon>
        </v-btn>
        <span>New document</span>
      </v-tooltip>
    </v-flex>
  </v-layout>
  <h3>Filter</h3>
  <v-layout row wrap>
    <v-flex sm4 xs6>
      <v-select :items="catchoices" label="Category" v-model="category" 
        @change="getDocuments" />
      <v-select :items="topicchoices" label="Topic" v-model="topic" 
        @change="getDocuments" />
    </v-flex>
    <v-flex sm4 xs6>
      <v-select :items="localechoices" label="Locale" v-model="locale" 
        @change="getDocuments" />
      <v-select :items="doctypechoices" label="Doc. type" v-model="doctype" 
        @change="getDocuments" />
    </v-flex>
  </v-layout>

  <v-data-table :items="documents" class="elevation-1" :headers="headers"
                :rows-per-page-items="[25,50,100]" :pagination.sync="pagination">
    <template slot="headers" slot-scope="props" >
      <th v-for="header in props.headers" :key="header.text"
          :class="headerClasses(header)" @click="changeSort(header)">
        {{ header.text }}
        <v-icon small v-show="header.sortable">arrow_upward</v-icon>
      </th>
      <th class="text-xs-left">Actions</th>
    </template>
    <template slot="items" slot-scope="props">
      <td>{{ props.item.category }}</td>
      <td>{{ props.item.topic }}</td>
      <td>{{ props.item.topicdate.split(' ')[0] }}</td>
      <td>{{ props.item.locale }}</td>
      <td>{{ props.item.doctype }}</td>
      <td>
        <v-icon class="mr-1" @click="editDocument(props.item)">edit</v-icon>
        <v-icon class="mr-1" @click="deleteDocument(props.item)">cancel</v-icon>
      </td>
    </template>
  </v-data-table>
  <v-dialog v-model="confirmdelete" max-width="260">
    <v-card>
      <v-card-title class="headline">Deleting document?</v-card-title>
      <v-card-text>
        Are you sure to delete the document: {{document.name}}
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="green darken-1" flat="flat" @click="confirmdelete = false">
          Cancel
        </v-btn>
        <v-btn color="green darken-1" flat="flat" @click="dodelete">
          Delete
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</v-container>
</template>

<script>

import api from '../util/api'
import dc from '../util/doctype'

export default {
  name: "MgmtDocumentsList",

  props: ['ts', 'selection'],

  computed: {
    headers () { return [
      {
        text: 'Category',
        align: 'left',
        sortable: true,
        value: 'name'
      },
      {
        text: 'Topic',
        align: 'left',
        sortable: true,
        value: 'name'
      },
      {
        text: 'Topic date',
        align: 'left',
        sortable: true,
        value: 'topicdate'
      },
      {
        text: 'Locale',
        align: 'left',
        sortable: true,
        value: 'locale'
      },
      {
        text: 'Doc. type',
        align: 'left',
        sortable: true,
        value: 'doctype'
      },
    ]},

  },


  data () {return {
    all: [{value:'', text:'-- not filtered --'}],
    category: '',
    catchoices: [],
    confirmdelete: false,
    doctype: '',
    doctypechoices: [],
    documents: [],
    document: {},
    locale: '',
    localechoices: [],
    pagination: {
      sortBy: 'name',
      descending: false,
    },
    topic: '',
    topicchoices: [],
  }},

  methods: {

    changeSort (header) {
      if (!header.sortable) return;
      if (this.pagination.sortBy === header.value) {
        this.pagination.descending = !this.pagination.descending
      } else {
        this.pagination.sortBy = header.value;
        this.pagination.descending = false
      }
    },

    deleteDocument (document) {
      this.document = document;
      this.confirmdelete = true;
    },

    dodelete () {
      api('deleteDocument', {id: this.document.id}).then(
        function(){
          this.confirmdelete = false;
          this.$emit('update', {section: 'list', reload: true})
        }.bind(this), 
        function(data){
          this.confirmdelete = false;
          console.error("cannot delete", data);
        }.bind(this)
      )
    },

    editDocument (d) {
      this.$emit('update', {section: 'edit', document: d});
    },

    getDocuments () {
      api('getDocuments', {
        topic: this.topic,
        category: this.category,
        locale: this.locale,
        doctype: this.doctype,
      }).then(
        function(data) {
          this.documents = data.documents;
        }.bind(this)
      );
    },

    gotoAdd () {
        this.$emit('update', {section: 'add'})
    },

    headerClasses (header) {
      let hc = ['column'];
      hc.push(header.align ? 'text-xs-' + header.align : 'text-xs-left');
      hc.push(header.sortable ? 'sortable': '');
      hc.push(this.pagination.descending ? 'desc' : 'asc');
      hc.push(header.value === this.pagination.sortBy ? 'active' : '');
      return hc;
    },

  },

  mounted () {
    this.getDocuments();
    this.catchoices = this.all.concat(dc.catchoices);
    this.topicchoices = this.all.concat(dc.topicchoices);
    this.localechoices = this.all.concat(dc.localechoices);
    this.doctypechoices = this.all.concat(dc.doctypechoices);
  },

  watch: {
    ts: function(){
      this.getDocuments();
    }
  }

}
</script>

<style scoped>

</style>
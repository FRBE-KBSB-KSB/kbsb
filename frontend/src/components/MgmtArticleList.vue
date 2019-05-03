<template>
<v-container fluid grid-list-md class="elevation-1">
  <v-layout row>
    <v-flex>
        <h1>Management Articles</h1>
    </v-flex>
    <v-flex>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="gotoAdd" slot="activator">
          <v-icon>add</v-icon>
        </v-btn>
        <span>New article</span>
      </v-tooltip>
    </v-flex>
  </v-layout>

  <v-layout row wrap>
    <v-flex sm4 xs6>
      <v-text-field append-icon="search" @click:append="search" v-model="ss" />
    </v-flex>

  </v-layout>

  <v-data-table :items="articles" class="elevation-1" :headers="headers"
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
      <td>{{ props.item.id }}</td>
      <td>{{ props.item.maintitle }}</td>
      <td>{{ props.item.status }}</td>
      <td class="text-xs-center">{{ props.item.category }}</td>
      <td>
        <v-icon class="mr-1" @click="editArticle(props.item)">edit</v-icon>
        <v-icon class="mr-1" @click="deleteArticle(props.item)">cancel</v-icon>
      </td>
    </template>
  </v-data-table>
  <v-dialog v-model="confirmdelete" max-width="260">
    <v-card>
      <v-card-title class="headline">Deleting article?</v-card-title>
      <v-card-text>
        Are you sure to delete the article: {{article.maintitle}}
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

export default {
  name: "MgmtArticlesList",

  props: ['ts', 'selection'],

  computed: {
    headers () { return [
      {
        text: 'ID',
        align: 'left',
        sortable: true,
        value: 'id'
      },
      {
        text: 'Main title',
        align: 'left',
        sortable: true,
        value: 'main_title'
      },
      {
        text: 'Status',
        align: 'left',
        sortable: true,
        value: 'status'
      },
    ]},

  },


  data () {return {
    articles: [],
    article: {},
    confirmdelete: false,
    pagination: {
      sortBy: 'main_title',
      descending: false,
    },
    ss: '',
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

    deleteArticle (article) {
      this.article = article;
      this.confirmdelete = true;
    },

    dodelete () {
      api('deleteArticle', {id: this.article.id}).then(
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

    editArticle (article) {
      this.$emit('update', {section: 'edit', article: article});
    },

    getArticles () {
      api('getArticles', {
      }).then(
        function(data) {
          this.articles = data.articles;
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

    search (){

    },

  },

  mounted () {
    this.getArticles();
  },

  watch: {
    ts: function(){
      this.getArticles();
    }
  }

}
</script>

<style scoped>

</style>
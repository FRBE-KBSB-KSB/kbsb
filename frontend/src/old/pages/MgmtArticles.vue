<template>
<v-container fluid>

  <mgmt-article-list @update="update($event)" v-show="section == 'list'" 
    :selection="selection"  :ts="ts" />
  <mgmt-article-edit @update="update($event)" v-if="section == 'edit'"
    :article="article" :ts="ts"/>
  <mgmt-article-add @update="update($event)" v-if="section == 'add'"/>

  <v-snackbar v-model="snackbar" :timeout="timeout" bottom>
    {{ snacktext }}
    <v-btn flat @click="snackbar = false">
      <v-icon>cancel</v-icon>
    </v-btn>
  </v-snackbar>

</v-container>
</template>

<script>

import MgmtArticleList from '../components/MgmtArticleList'
import MgmtArticleEdit from '../components/MgmtArticleEdit'
import MgmtArticleAdd from '../components/MgmtArticleAdd'

export default {

  name: "MgmtArticles",

  data () {return {
    section: 'list',
    selection: [],
    snackbar: false,
    snacktext: '',
    article: {},
    ts: new Date(),
    timeout: 4000,
  }},

  components: {
    MgmtArticleList,
    MgmtArticleAdd,
    MgmtArticleEdit,
  },

  methods: {
    update (e) {
      console.log('update', e);
      if (e.section)
        this.section = e.section;
      if (e.article)
        this.article = e.article;
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
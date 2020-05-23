<template>

  <v-container class="mt-1 markedcontent">
    <h1 v-html="title" />
    <div v-html="intro" class="mt-1"/>
    <hr/>
    <div v-html="body" class="mt-1" />
  </v-container>

</template>

<script>
import {mapState} from "vuex"
import marked from 'marked'

export default {

  name: 'CmsSimplePage',

  data () {return {
    page: {},
  }},

  computed: {
    body () { 
      return marked(this.page.body || '' )
    },
    intro () { 
      return marked(this.page.intro || '' )
    },
    title () { 
      return this.page.title || '' 
    },
    ...mapState(['api', 'locale', 'slug']),

  },

  methods: {
    
    getContent () {
      let self=this;
      this.api.get_localized_page({
        slug: this.slug,
        locale: this.locale,
      }).then(
        function(data){
          self.page =  data.obj.page;
        },
        function(data){
          console.error('could not fetch localized page', data)
        }
      );
    },

  },

  mounted () {
    this.getContent();
  },

  watch: {
    locale: function (nv, ov) {
      console.log('watch locale', nv, ov)
      this.$router.push('/page/' + this.slug + '/' + nv)
    },
    slug: function (nv, ov) {
      console.log('watch slug', nv, ov)
      this.$router.push('/page/' + nv + '/' + this.locale)
    },
  }

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

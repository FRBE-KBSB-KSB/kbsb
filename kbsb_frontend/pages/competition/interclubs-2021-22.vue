<template>
  <v-container>
    <h1>Interclub 2021 - 2022</h1>
    <div class="mt-1" v-html="intro" />
    <div class="mt-1" v-html="body" />
  </v-container>
</template>

<script>

import { marked } from 'marked'

export default {
  layout: 'landing',

  data () {
    return {
      page: {}
    }
  },

  computed: {

    body () {
      let pt = ''
      if (this.page.body) {
        pt = this.page.body.default.value
        if (this.page.body[this.$i18n.locale]) { pt = this.page.body[this.$i18n.locale].value }
      }
      return marked(pt)
    },

    intro () {
      let pt = ''
      if (this.page.intro) {
        pt = this.page.intro.default.value
        if (this.page.intro[this.$i18n.locale]) { pt = this.page.intro[this.$i18n.locale].value }
      }
      return marked(pt)
    }
  },

  mounted () {
    console.log('ic 2122 mounted')
    this.getContent()
  },

  methods: {

    getContent () {
      this.$api.page.anon_slug_page({ slug: 'interclub-2021-22' }).then(
        (resp) => {
          console.log('ic resp', resp)
          this.page = resp.data
        },
        resp => (console.error('could not fetch articles', resp))
      )
    }

  }

}
</script>

<style>
h1:after
{
    content:' ';
    display: block;
    border:1px solid #aaa;
    margin-bottom: 1em;
}
.nuxt-content td, .nuxt-content th {
  padding: 8px;
  border: 1px solid #ddd;
}
.nuxt-content table {
  border-collapse: collapse;
}
.nuxt-content ul , .nuxt-content ol, .nuxt-content h2, .nuxt-content h3 {
    margin-bottom: 0.5em;
}
</style>

<template>
  <v-container>
    <h1>{{ title }}</h1>
    <div class="mt-1" v-html="intro" />
    <div class="mt-1" v-html="body" />
  </v-container>
</template>

<script>

import { marked } from 'marked'

export default {

  name: 'Article',

  layout: 'landing',

  head: {
    title: 'Article',
  },

  data() {
    return {
      page: {}
    }
  },


  computed: {

    body() {
      let pt = ''
      if (this.page.body) {
        pt = this.page.body.default.value
        if (this.page.body[this.$i18n.locale]) {
          pt = this.page.body[this.$i18n.locale].value
        }
      }
      return marked(pt)
    },

    intro() {
      let pt = ''
      if (this.page.intro) {
        pt = this.page.intro.default.value
        if (this.page.intro[this.$i18n.locale]) {
          pt = this.page.intro[this.$i18n.locale].value
        }
      }
      return marked(pt)
    },

    title() {
      let pt = ''
      const t = this.page.title
      const locale = this.$i18n.locale
      if (t) {
        pt = t.default.value
        if (t[locale]) {
          pt = t[locale].value
        }
      }
      return pt
    }

  },

  mounted() {
    this.getContent()
  },

  methods: {

    async getContent() {
      try {
        const resp = await this.$api.page.anon_slug_page({ slug: this.$route.query.slug })
        console.log('article', resp)
        this.page = resp.data
        console.log('article processed')
      } catch (error) {
        console.error('could not fetch article', error)
      }
    }

  }

}
</script>

<style>
h1:after {
  content: ' ';
  display: block;
  border: 1px solid #aaa;
  margin-bottom: 1em;
}

.nuxt-content td,
.nuxt-content th {
  padding: 8px;
  border: 1px solid #ddd;
}

.nuxt-content table {
  border-collapse: collapse;
}

.nuxt-content ul,
.nuxt-content ol,
.nuxt-content h2,
.nuxt-content h3 {
  margin-bottom: 0.5em;
}
</style>

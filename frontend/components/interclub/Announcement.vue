<template>
  <v-container>
    <v-card v-for="a in ann" :key="a.id">
      <v-card-title>
        {{ a.title }}
      </v-card-title>
      <v-card-text>
        <div class="d-flex">
          <div>{{ a.publicationdate}}:&nbsp;</div>
          <div v-html="a.intro"></div>
        </div>
        <div v-html="a.body" />
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>

import { marked } from 'marked'
import { notitle, nointro } from '@/util/cms'

export default {

  name: 'Enrollment',

  data() {
    return {
      ann: []
    }
  },

  methods: {

    async get_announcements() {
      console.log('fetching announcements', this.$api)
      try {
        const reply = await this.$api.interclub.get_announcements()
        this.readAccouncements(reply.data.items)
      }
      catch (error) {
        const reply = error.response
        console.error('getting announcements', reply)
        this.$root.$emit('snackbar', { text: this.$t('Getting interclub announcements failed') })
      }
    },

    readAccouncements(announcements) {
      console.log('reading announcements', announcements)
      const locale = this.$i18n.locale
      this.ann = []
      announcements.forEach((a, index) => {
        console.log('a', a)
        const b = {}
        if (!a.title[locale] || !a.title[locale].value || !a.title[locale].value.length) {
          b.title = notitle[locale]
        } else {
          b.title = a.title[locale].value
        }
        if (!a.intro[locale] || !a.intro[locale].value || !a.intro[locale].value.length) {
          b.intro = marked.parse(nointro[this.$i18n.locale])
        } else {
          b.intro = marked.parse(a.intro[locale].value)
        }
        if (!a.body[locale] || !a.body[locale].value || !a.body[locale].value.length) {
          b.body = ""
        } else {
          b.body = marked.parse(a.body[locale].value)
        }
        b.publicationdate = a.publicationdate
        this.ann.push(b)
      })
    }
  },

  mounted() {
    this.get_announcements()
  },

}
</script>
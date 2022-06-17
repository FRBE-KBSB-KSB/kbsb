<template>
  <v-container>
    <v-card>
      <v-card-title color="grey lighten-4">
        <h2>New News Article</h2>
        <v-spacer />
        <v-tooltip bottom>
          <template #activator="{ on }">
            <v-btn
              fab
              outlined
              color="deep-purple"
              v-on="on"
              @click="back()"
            >
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
          </template>
          <span>Go Back</span>
        </v-tooltip>
        <v-tooltip bottom>
          <template #activator="{ on }">
            <v-btn
              fab
              outlined
              color="deep-purple"
              v-on="on"
              @click="save()"
            >
              <v-icon>mdi-content-save</v-icon>
            </v-btn>
          </template>
          <span>Save changes</span>
        </v-tooltip>
      </v-card-title>
      <v-card-text>
        <v-text-field v-model="name" label="Name" />
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>

import { doctypes } from '@/util/cms'

export default {

  name: 'Pageedit',

  layout: 'mgmt',

  data () {
    return {
      name: '',
      doctype: null,
      doctypes
    }
  },

  computed: {
    token () { return this.$store.state.token.value }
  },

  methods: {

    back () {
      this.$router.push('/mgmt/pagelist')
    },

    async save () {
      try {
        const resp = await this.$api.page.add_page({
          doctype: 'article',
          name: this.name,
          locale: 'nl',
          token: this.token
        })
        console.log('page created', resp.data)
        this.$router.push('/mgmt/pageedit?id=' + resp.data)
      } catch (error) {
        const resp = error.response
        console.error('getting getPages', resp)
        if (resp.status === 401) {
          this.$router.push('/mgmt/login')
        } else {
          this.$root.$emit('snackbar', { text: 'Adding page failed', reason: resp.data.detail })
        }
      }
    }

  }

}
</script>

<style scoped>
.bordermd {
  border: 1px solid grey;
}
</style>

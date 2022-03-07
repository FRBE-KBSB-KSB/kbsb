<template>
  <v-container>
    <v-card>
      <v-card-title color="grey lighten-4">
        <h2>Edit Page: {{ p.name }}</h2>
        <v-spacer />
        <v-tooltip bottom>
          <template #activator="{ on }">
            <v-btn
              slot="activator"
              outlined
              fab
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
              slot="activator"
              outlined
              fab
              color="deep-purple"
              v-on="on"
              @click="save()"
            >
              <v-icon>mdi-content-save</v-icon>
            </v-btn>
          </template>
          <span>Save page</span>
        </v-tooltip>
        <v-tooltip bottom>
          <template #activator="{ on }">
            <v-btn
              slot="activator"
              outlined
              fab
              color="deep-purple"
              v-on="on"
              @click="remove()"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>
          <span>Delete page</span>
        </v-tooltip>
      </v-card-title>
      <v-card-text>
        <v-tabs class="elevation-2">
          <v-tab>Common</v-tab>
          <v-tab v-for="l in languages" :key="l">
            {{ l }}
          </v-tab>
          <v-tab-item>
            <v-container>
              <v-row>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="p.name" label="Name" />
                  <v-text-field v-model="p.created_by" label="Owner" />
                  <v-text-field v-model="p.slug" label="Slug" />
                  <v-select v-model="p.doctype" :items="doctypes" label="Document type" />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-checkbox v-model="p.enabled" label="Enabled" />
                  <p>Page created: {{ p._creationtime }}</p>
                  <p>Page modified: {{ p._modificationtime }}</p>
                  <v-menu
                    v-model="menu_published"
                    :close-on-content-click="false"
                    :nudge-right="40"
                    transition="scale-transition"
                    offset-y
                    min-width="290px"
                  >
                    <template #activator="{ on }">
                      <v-text-field
                        v-model="p.publicationdate"
                        label="Publication date"
                        prepend-icon="mdi-calendar-range"
                        readonly
                        v-on="on"
                      />
                    </template>
                    <v-date-picker v-model="p.publicationdate" color="deep-purple" @input="menu_published = false" />
                  </v-menu>
                  <v-menu
                    v-model="menu_expired"
                    :close-on-content-click="false"
                    :nudge-right="40"
                    transition="scale-transition"
                    offset-y
                    min-width="290px"
                  >
                    <template #activator="{ on }">
                      <v-text-field
                        v-model="p.expirationdate"
                        label="Expiry date"
                        prepend-icon="mdi-calendar-range"
                        readonly
                        v-on="on"
                      />
                    </template>
                    <v-date-picker v-model="p.expirationdate" color="deep-purple" @input="menu_expired = false" />
                  </v-menu>
                </v-col>
              </v-row>
            </v-container>
          </v-tab-item>
          <v-tab-item v-for="l in languages" :key="l">
            <v-checkbox v-model="enabled[l]" :label="l" class="pl-5" />
            <v-text-field v-model="titles[l]" class="mx-3" label="Title" />
            <v-text-field v-model="intros[l]" class="mx-3" label="Intro" />
            <v-textarea v-model="bodys[l]" class="mx-3" solo label="Body" rows="15" />
          </v-tab-item>
        </v-tabs>
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
      activetab: '',
      dialogDelete: false,
      doctypes,
      enabled: { en: false, nl: false, fr: false, de: false },
      languages: ['en', 'nl', 'fr', 'de'],
      idpage: this.$route.query.id,
      menu_published: false,
      menu_expired: false,
      p: {},
      intros: { en: '', nl: '', fr: '', de: '' },
      titles: { en: '', nl: '', fr: '', de: '', default: '' },
      bodys: { en: '', nl: '', fr: '', de: '' }
    }
  },

  computed: {
    enabledLang () {
      const la = []; const self = this
      this.lang.available.forEach(function (l) {
        if (self.lang.enabled[l] === true) {
          la.push(l)
        }
      })
      return la
    },
    token () { return this.$store.state.token.value }
  },

  mounted () {
    this.getPage()
  },

  methods: {

    back () {
      this.$router.push('/mgmt/pagelist')
    },

    async getPage () {
      try {
        const resp = await this.$api.page.get_page({
          id: this.$route.query.id,
          token: this.token
        })
        this.readPage(resp.data)
      } catch (error) {
        const resp = error.response
        console.error('getting getPages', resp)
        if (resp.status === 401) {
          this.$router.push('/mgmt/login')
        } else {
          this.$root.$emit('snackbar', { text: 'Getting page failed', reason: resp.data.detail })
        }
      }
    },

    readPage (page) {
      const self = this; let ls
      this.p = { ...page }
      this.enabled = { en: false, nl: false, fr: false, de: false }
      ls = this.p.languages
      this.activetab = ls[0]
      this.titles.default = this.p.title.default.value
      this.languages.forEach(function (l) {
        self.bodys[l] = self.p.body.default.value
        self.titles[l] = self.p.title.default.value
        self.intros[l] = self.p.intro.default.value
      })
      ls.forEach(function (l) {
        self.enabled[l] = true
        self.bodys[l] = self.p.body[l]
          ? self.p.body[l].value
          : self.p.bodys.default.value
        self.titles[l] = self.p.title[l]
          ? self.p.title[l].value
          : self.p.title.default.value
        self.intros[l] = self.p.intro[l]
          ? self.p.intro[l].value
          : self.p.intro.default.value
      })
    },

    async remove () {
      if (window.confirm('Are you sure to delete page "' + this.p.name + '"?')) {
        try {
          await this.$api.page.delete_page({
            id: this.$route.query.id,
            token: this.token
          })
          this.$root.$emit('snackbar', { text: 'Page deleted' })
          this.$router.push('/mgmt/pagelist')
        } catch (error) {
          const resp = error.response
          console.error('getting getPages', resp)
          if (resp.status === 401) {
            this.$router.push('/mgmt/login')
          } else {
            this.$root.$emit('snackbar', { text: 'Deleting page failed', reason: resp.data.detail })
          }
        }
      }
    },

    async save () {
      const self = this; const ls = []
      this.languages.forEach(function (l) {
        if (self.enabled[l]) {
          ls.push(l)
          if (!self.p.body[l]) {
            self.p.body[l] = { ...self.p.body.default }
          }
          self.p.body[l].value = self.bodys[l]
          if (!self.p.intro[l]) {
            self.p.intro[l] = { ...self.p.intro.default }
          }
          self.p.intro[l].value = self.intros[l]
          if (!self.p.title[l]) {
            self.p.title[l] = { ...self.p.title.default }
          }
          self.p.title[l].value = self.titles[l]
        } else {
          delete self.p.body[l]
          delete self.p.intro[l]
          delete self.p.title[l]
        }
      })
      try {
        await this.$api.page.update_page({
          id: this.$route.query.id,
          body: this.p.body,
          component: this.p.component,
          doctype: this.p.doctype,
          enabled: this.p.enabled,
          expirationdate: this.p.expirationdate,
          intro: this.p.intro,
          languages: ls,
          name: this.p.name,
          owner: this.p.owner,
          publicationdate: this.p.publicationdate,
          slug: this.p.slug,
          title: this.p.title,
          token: this.token
        })
        console.log('save successful')
        this.$root.$emit('snackbar', { text: 'Page saved' })
      } catch (error) {
        const resp = error.response
        console.error('getting getPages', resp)
        if (resp.status === 401) {
          this.$router.push('/mgmt/login')
        } else {
          this.$root.$emit('snackbar', { text: 'Saving page failed', reason: resp.data.detail })
        }
      }
    },

    toggleLang (l) {
      this.p.languages = this.enabledLang
      if (l in this.p.page_i18n_fields === false) {
        this.p.page_i18n_fields[l] = {
          body: '',
          intro: '',
          title: ''
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

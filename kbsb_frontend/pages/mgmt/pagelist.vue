<template>
  <v-container>
    <h1>Management News Articles</h1>
    <v-data-table :headers="headers" :items="filteredpages" :footer-props="footerProps"
      class="elevation-1" :sort-by="['publicationdate', 'name']">
      <template #top>
        <v-card color="grey lighten-4">
          <v-card-title>
            <v-row class="px-2">
              <v-spacer />
              <v-tooltip bottom>
                <template #activator="{ on }">
                  <v-btn fab outlined color="deep-purple" v-on="on" @click="addPage()">
                    <v-icon>mdi-plus</v-icon>
                  </v-btn>
                </template>
                Add Page
              </v-tooltip>
              <v-tooltip bottom>
                <template #activator="{ on }">
                  <v-btn fab outlined color="deep-purple" v-on="on" @click="backupPages()">
                    <v-icon>mdi-download-multiple</v-icon>
                  </v-btn>
                </template>
                Backup Pages
              </v-tooltip>
            </v-row>
          </v-card-title>
        </v-card>
      </template>
      <template #item.action="{ item }">
        <v-tooltip bottom>
          <template #activator="{ on }">
            <v-icon small class="mr-2" v-on="on" @click="editPage(item)">
              mdi-pencil
            </v-icon>
          </template>
          Edit Page
        </v-tooltip>
      </template>
      <template #no-data>
        No pages found.
      </template>
    </v-data-table>
  </v-container>
</template>

<script>

export default {

  name: 'Pagelist',

  layout: 'mgmt',

  data() {
    return {
      filter: {},
      footerProps: {
        itemsPerPageOptions: [20, 50, -1],
        itemsPerPage: 20
      },
      headers: [
        {
          text: 'Name', value: 'name'
        },
        {
          text: 'Publication Date', value: 'publicationdate'
        },
        {
          text: 'Doctype', value: 'doctype'
        },
        {
          text: 'Enabled', value: 'enabled'
        },
        {
          text: 'Actions', value: 'action', sortable: false
        }
      ],
      pages: []
    }
  },

  computed: {
    filteredpages() {
      return this.pages
      // const pa = []
      // if (!this.filter.normal && !this.filter.article && !this.filter.app) {
      //   return this.pages
      // }
      // this.pages.forEach((p) => {
      //   if (p.doctype === 'normal-page' && this.filter.normal) {
      //     pa.push(p)
      //     return
      //   }
      //   if (p.doctype === 'article' && this.filter.article) {
      //     pa.push(p)
      //     return
      //   }
      //   if (p.doctype === 'app-page' && this.filter.app) {
      //     pa.push(p)
      //   }
      // })
      // return pa
    },
    token() { return this.$store.state.newlogin.value }
  },

  head: {
    title: 'Management Articles',
  },

  mounted() {
    this.getPages()
  },

  methods: {

    addPage() {
      this.$router.push('/mgmt/pageadd')
    },

    editPage(item) {
      this.$router.push('/mgmt/pageedit/?id=' + item.id)
    },

    async getPages() {
      try {
        const resp = await this.$api.page.get_pages({
          token: this.token
        })
        this.pages = resp.data.items
      } catch (error) {
        const resp = error.response
        console.error('getting getPages', resp)
        if (resp.status === 401) {
          this.gotoLogin()
        } else {
          this.$root.$emit('snackbar', { text: 'Getting pages failed', reason: resp.data.detail })
        }
      }
    },

    gotoLogin() {
      this.$router.push('/mgmt/login?url=__mgmt__pagelist')
    },

  }



}
</script>

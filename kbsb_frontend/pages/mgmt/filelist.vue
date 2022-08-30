<template>
  <v-container>
    <h1>Management Files</h1>
    <v-data-table :headers="headers" :items="files" :footer-props="footerProps" class="elevation-1"
      :sort-by="['name']">
      <template #top>
        <v-toolbar flat color="white">
          <v-toolbar-title>
            Files
          </v-toolbar-title>
          <v-spacer />
          <v-tooltip bottom>
            <template #activator="{ on }">
              <v-btn fab outlined color="deep-purple" v-on="on" @click="addFile()">
                <v-icon>mdi-plus</v-icon>
              </v-btn>
            </template>
            <span>Add File</span>
          </v-tooltip>
        </v-toolbar>
      </template>
      <template #item.action="{ item }">
        <v-icon small class="mr-2" @click="editFile(item)">
          mdi-pencil
        </v-icon>
      </template>
      <template #item.topic_ts="{ item }">
        {{ item.topic_ts }}
      </template>
      <template #no-data>
        No files yet.
      </template>
    </v-data-table>
  </v-container>
</template>

<script>

export default {

  name: 'Filelist',

  layout: 'mgmt',

  head: {
    title: 'Management Files',
  },

  data() {
    return {
      headers: [
        {
          text: 'Name', value: 'name'
        },
        {
          text: 'Topic', value: 'topic'
        },
        {
          text: 'Topic timestamp', value: 'topicdate'
        },
        {
          text: 'Actions', value: 'action', sortable: false
        }
      ],
      files: [],
      footerProps: {
        itemsPerPageOptions: [20, 50, -1],
        itemsPerPage: 20
      }
    }
  },

  computed: {
    token() { return this.$store.state.newlogin.value }
  },

  mounted() {
    this.getFiles()
  },

  methods: {

    addFile() {
      this.$router.push('/mgmt/fileadd')
    },

    editFile(item) {
      this.$router.push('/mgmt/fileedit/?id=' + item.id)
    },

    async getFiles() {
      try {
        const resp = await this.$api.file.get_files({
          token: this.token
        })
        this.files = resp.data.files
      } catch (error) {
        const resp = error.response
        console.error('getting getFiles', resp)
        if (resp.status === 401) {
          this.$router.push('/mgmt/login')
        } else {
          this.$root.$emit('snackbar', { text: 'Getting files failed', reason: resp.data.detail })
        }
      }
    }

  }

}
</script>

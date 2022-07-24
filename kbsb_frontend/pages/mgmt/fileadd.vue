<template>
  <v-container>
    <v-row>
      <v-col cols="9">
        <h1>New Page</h1>
      </v-col>
      <v-col cols="3">
        <v-tooltip bottom>
          <template #activator="{ on }">
            <v-btn fab outlined color="deep-purple" v-on="on" @click="back()">
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
          </template>
          <span>Go Back</span>
        </v-tooltip>
        <v-tooltip bottom>
          <template #activator="{ on }">
            <v-btn fab outlined color="deep-purple" v-on="on" @click="save()">
              <v-icon>mdi-content-save</v-icon>
            </v-btn>
          </template>
          <span>Save changes</span>
        </v-tooltip>
      </v-col>
    </v-row>
    <h4>Drop Area</h4>
    <file-pond ref="pond" class-name="dropbox" @addfile="handleFile" />
    <v-select v-model="topic" :items="topictypes" label="Topic" />

  </v-container>
</template>

<script>
import 'filepond/dist/filepond.min.css'
import vueFilePond from 'vue-filepond'
import { topictypes } from '@/util/cms'

const FilePond = vueFilePond()

export default {

  name: 'Fileedit',

  components: {
    FilePond
  },

  layout: 'mgmt',

  data() {
    return {
      content: '',
      f: {},
      name: '',
      topictypes,
      topic: 'Report Board Meeting'
    }
  },

  computed: {
    token() { return this.$store.state.newlogin.value }
  },

  methods: {

    back() {
      this.$router.push('/mgmt/filelist')
    },

    handleFile(err, file) {
      if (err) {
        console.error(err)
        return
      }
      const reader = new FileReader()
      console.log('file dropped', file)
      this.name = file.filename
      reader.onload = () => {
        this.content = reader.result.split(',')[1]
      }
      reader.readAsDataURL(file.file)
    },

    async save() {
      try {
        const resp = await this.$api.file.add_file({
          name: this.name,
          content: this.content,
          topic: this.topic,
          token: this.token
        })
        console.log('file added', resp.data)
        this.$router.push('/mgmt/fileedit?id=' + resp.data)
      } catch (error) {
        const resp = error.response
        console.error('getting add_file', resp)
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

.dropbox {
  width: 100%;
  height: 100px;
}

</style>

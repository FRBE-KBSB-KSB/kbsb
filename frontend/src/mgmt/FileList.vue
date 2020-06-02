<template>

<v-container>
  <h1>Management Files</h1>
  <v-data-table :headers="headers" :items="files"
      class="elevation-1" sort-by="fullname">
    <template v-slot:top>
      <v-toolbar flat color="white">
        <v-toolbar-title>
          Files
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-tooltip bottom >
          <template v-slot:activator="{ on }">
            <v-btn v-on="on" @click="addFile()" fab outlined 
                  color="deep-purple">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </template>
          <span>Add File</span>
         </v-tooltip>
      </v-toolbar>
    </template>
    <template v-slot:item.action="{ item }">
      <v-icon small class="mr-2"  @click="editFile(item)" >
        mdi-pencil
      </v-icon>
    </template>
    <template v-slot:no-data>
      No files yet.
    </template>            
  </v-data-table>
</v-container>

</template>

<script>

import { mapState } from 'vuex'
import { bearertoken } from "@/util/token"


export default {

  name: 'FileList',

  data () {return {
    headers: [
      {
        text: "Name", value: 'name'
      },
      {
        text: "Topic", value: 'topic'
      },
      {
        text: "Topic timestamp", value: 'topic_ts'
      },
      {
        text: 'Actions', value: 'action', sortable: false
      }
    ],    
    files: [],
  }},

  computed: {
    ...mapState(['token', 'api'])
  },


  methods: {

    addFile () {
      this.$router.push('/mgmt/file/add')
    },

    editFile (item) {
      this.$router.push('/mgmt/file/edit/'  + item.id)
    },
    
    getFiles() {
      let self=this;
      console.log('getFiles bearer ', bearertoken(this.token))
      this.api.get_files(
        {},
        {securities: bearertoken(this.token)},
      ).then(
        function(data) {
          self.files = data.obj.files;
          self.files.forEach(function(p){
            p.topic_ts = (new Date(p.created_ts)).toLocaleString();
          })
        },
        function(data){
          if (data.status == 401) {
            self.$router.push('/mgmt/login')
          }
          else {
            console.error('getting getFiles', data);
          self.$root.$emit('snackbar', {text: 'Getting files failed', reason: data})            
          }
        }
      );
    }
    
  },

  mounted () {
    this.getFiles();
  },  

}
</script>

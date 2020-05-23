<template>

<v-container>
  <h1>Management Pages</h1>
  <v-data-table :headers="headers" :items="pages"
      class="elevation-1" sort-by="fullname">
    <template v-slot:top>
      <v-toolbar flat color="white">
        <v-toolbar-title>
          Pages
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-tooltip bottom >
          <template v-slot:activator="{ on }">
            <v-btn v-on="on" @click="addPage()" fab outlined 
                  color="deep-purple">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </template>
          <span>Add Page</span>
         </v-tooltip>
      </v-toolbar>
    </template>
    <template v-slot:item.action="{ item }">
      <v-icon small class="mr-2"  @click="editPage(item)" >
        mdi-pencil
      </v-icon>
    </template>
    <template v-slot:no-data>
      No pages yet.
    </template>            
  </v-data-table>
</v-container>

</template>

<script>

import { mapState } from 'vuex'
import { oAuth2token } from "@/util/token"


export default {

  name: 'PageList',

  data () {return {
    headers: [
      {
        text: "Name", value: 'name'
      },
      {
        text: "Created", value: 'created_ts'
      },
      {
        text: "Modified", value: 'modified_ts'
      },
      {
        text: 'Actions', value: 'action', sortable: false
      }
    ],    
    pages: [],
  }},

  computed: {
    ...mapState(['token', 'api'])
  },


  methods: {

    addPage () {
      this.$router.push('/mgmt/page/add')
    },

    editPage (item) {
      this.$router.push('/mgmt/page/edit/'  + item.id)
    },
    
    getPages() {
      let self=this;
      this.api.get_pages({},
        {securities: oAuth2token(this.token)},
      ).then(
        function(data) {
          self.pages = data.obj.pages;
          self.pages.forEach(function(p){
            p.created_ts = (new Date(p.created_ts)).toLocaleString();
            p.modified_ts = (new Date(p.modified_ts)).toLocaleString();
          })
        },
        function(data){
          if (data.status == 401) {
            self.$router.push('/mgmt/login')
          }
          else {
            console.error('getting getPages', data);
          }
        }
      );
    }
    
  },

  mounted () {
    this.getPages();
  },  

}
</script>

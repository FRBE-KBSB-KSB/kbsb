<template>

<v-container>
  <h1>Management Board Roles</h1>
  <v-data-table :headers="headers" :items="boardroles" :footer-props="footerProps"
      class="elevation-1" sort-by="name">
    <template v-slot:top>
      <v-toolbar flat color="white">
        <v-toolbar-title>
          Board Roles
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-tooltip bottom >
          <template v-slot:activator="{ on }">
            <v-btn v-on="on" @click="addBoardRole()" fab outlined 
                  color="deep-purple">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </template>
          <span>Add Board Role</span>
         </v-tooltip>
      </v-toolbar>
    </template>
    <template v-slot:item.action="{ item }">
      <v-icon small class="mr-2"  @click="editBoardRole(item)" >
        mdi-pencil
      </v-icon>
    </template>
    <template v-slot:item.topic_ts="{ item }">
      <date-formatted :date="item.topic_ts" fmt="ll" />
    </template>
    <template v-slot:no-data>
      No board roles yet.
    </template>            
  </v-data-table>
</v-container>

</template>

<script>

import { mapState } from 'vuex'
import { bearertoken } from "@/util/token"

export default {

  name: 'BoardRoleList',

  data () {return {
    headers: [
      {
        text: "Name", value: 'name'
      },
      {
        text: 'Actions', value: 'action', sortable: false
      }
    ],    
    boardroles: [],
    footerProps: {
      itemsPerPageOptions: [20,50,-1],
      itemsPerPage: 20,
    },

  }},

  computed: {
    ...mapState(['token', 'api'])
  },


  methods: {

    addBoardRole () {
      this.$router.push('/mgmt/boardrole/add')
    },

    editBoardRole (item) {
      this.$router.push('/mgmt/boardrole/edit/'  + item.id)
    },
    
    getBoardRoles() {
      let self=this;
      this.api.getBoardRoles(
        {},
        {securities: bearertoken(this.token)},
      ).then(
        function(data) {
          self.boardroles = data.obj.roles;
        },
        function(data){
          if (data.status == 401) {
            self.$router.push('/mgmt/login')
          } 
          else {
            console.error('getting getBoardRoles', data);
          self.$root.$emit('snackbar', {text: 'Getting boardroles failed', reason: data})            
          }
        }
      );
    }
    
  },

  mounted () {
    this.getBoardRoles();
  },  

}
</script>

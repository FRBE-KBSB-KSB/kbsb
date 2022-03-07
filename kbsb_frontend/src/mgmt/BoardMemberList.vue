<template>

<v-container>
  <h1>Management Board Members</h1>
  <v-data-table :headers="headers" :items="boardmembers" :footer-props="footerProps"
      class="elevation-1" sort-by="name">
    <template v-slot:top>
      <v-toolbar flat color="white">
        <v-toolbar-title>
          Board Members
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-tooltip bottom >
          <template v-slot:activator="{ on }">
            <v-btn v-on="on" @click="addBoardMember()" fab outlined 
                  color="deep-purple">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </template>
          <span>Add Board Member</span>
         </v-tooltip>
      </v-toolbar>
    </template>
    <template v-slot:item.action="{ item }">
      <v-icon small class="mr-2"  @click="editBoardMember(item)" >
        mdi-pencil
      </v-icon>
    </template>
    <template v-slot:item.topic_ts="{ item }">
      <date-formatted :date="item.topic_ts" fmt="ll" />
    </template>
    <template v-slot:no-data>
      No board members yet.
    </template>            
  </v-data-table>
</v-container>

</template>

<script>

import { mapState } from 'vuex'
import { bearertoken } from "@/util/token"

export default {

  name: 'BoardMemberList',

  data () {return {
    headers: [
      {
        text: "First name", value: 'first_name'
      },
      {
        text: "Last name", value: 'last_name'
      },
      {
        text: 'Actions', value: 'action', sortable: false
      }
    ],    
    boardmembers: [],
    footerProps: {
      itemsPerPageOptions: [20,50,-1],
      itemsPerPage: 20,
    },

  }},

  computed: {
    ...mapState(['token', 'api'])
  },


  methods: {

    addBoardMember () {
      this.$router.push('/mgmt/boardmember/add')
    },

    editBoardMember (item) {
      this.$router.push('/mgmt/boardmember/edit/'  + item.id)
    },
    
    getBoardMembers() {
      let self=this;
      this.api.getBoardMembers(
        {},
        {securities: bearertoken(this.token)},
      ).then(
        function(data) {
          self.boardmembers = data.obj.members;
        },
        function(data){
          if (data.status == 401) {
            self.$router.push('/mgmt/login')
          } 
          else {
            console.error('getting getBoardMembers', data);
            self.$root.$emit('snackbar', {text: 'Getting boardmembers failed', reason: data})            
          }
        }
      );
    }
    
  },

  mounted () {
    this.getBoardMembers();
  },  

}
</script>

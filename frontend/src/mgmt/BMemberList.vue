<template>

<v-container class="elevation-2">
  <h1>Management of board members</h1>
  <v-data-table :headers="headers" :items="members" :footer-props="footerprops"
       sort-by="fullname" :items-per-page="30">
    <template v-slot:top>
      <v-toolbar flat color="white">
        <v-toolbar-title>
          Members
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-tooltip bottom >
          <template v-slot:activator="{ on }">
            <v-btn v-on="on" @click="addMember()" fab outlined 
                  color="deep-purple">
              <v-icon>add</v-icon>
            </v-btn>
          </template>
          <span>Add Member</span>
         </v-tooltip>
      </v-toolbar>
    </template>
    <template v-slot:item.fullname="{ item }">
      {{ item.first_name }} {{ item.last_name }} 
    </template>    
    <template v-slot:item.action="{ item }">
      <v-icon small class="mr-2"  @click="editMember(item)" >
        edit
      </v-icon>
    </template>
    <template v-slot:no-data>
      No members yet.
    </template>            
  </v-data-table>
</v-container>

</template>

<script>

import { mapState } from 'vuex'


export default {

  name: 'BMemberList',

  data () {return {
    headers: [
      {
        text: "Full name", value: 'fullname'
      },
      {
        text: "Email", value: 'email'
      },
      {
        text: "Mobile", value: 'mobile'
      },
      {
        text: 'Actions', value: 'action', sortable: false
      }
    ],
    footerprops: {
      "items-per-page-options": [15,30,50,-1],
    },

    members: [],
  }},

  computed: {
    ...mapState(['token', 'api'])
  },


  methods: {
  
    addMember () {
      this.$router.push('/mgmt/bmember/add')
    },
  
    editMember (item) {
      this.$router.push('/mgmt/bmember/edit/'  + item.id)
    },

    fetchMembers(){
      let self = this;
      this.api.get_board_members().then(
        function(rc) {
          self.members = rc.obj.members;
        },
        function(rc){
          console.log('failed', rc)
          if (rc.status == 401) {
            self.$router.push('/mgmt/login')
          }
          else {
            // TODO snackbar
            console.error('get board members', rc);
          }
        }
      );
    },

  },

  mounted () {
    // make sure the api is loaded
    if (this.api) this.fetchMembers()
  },
  
  watch: {
    api: function() {
      this.fetchMembers()
    }
  },
 

}
</script>

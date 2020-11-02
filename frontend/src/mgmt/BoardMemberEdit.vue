<template>
<v-container class="elevation-1 mt-2">
  <v-row>
    <v-col cols=12 sm=6>
        <h1>Edit board member: {{ bm.first_name }}  {{ bm.last_name }} </h1>
    </v-col>
    <v-col col=12 sm=6>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" outlined fab color="deep-purple" @click="back()" 
              slot="activator">
            <v-icon>mdi-arrow-left</v-icon>
          </v-btn>
        </template>
        <span>Go Back</span>
      </v-tooltip>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" outlined fab color="deep-purple" @click="save()" 
              slot="activator">
            <v-icon>mdi-content-save</v-icon>
          </v-btn>
        </template>
        <span>Save board member properties</span>
      </v-tooltip>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" outlined fab color="deep-purple" @click="remove()" 
              slot="activator">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
        <span>Delete board member</span>
      </v-tooltip>
    </v-col>
  </v-row>
  <v-row>
    <v-col cols=12 sm=6>
      <v-text-field label="First name" v-model="bm.first_name" />
      <v-text-field label="Last name" v-model="bm.last_name" />
      <v-text-field label="E-mail" v-model="bm.email" />
      <v-text-field label="Mobile" v-model="bm.mobile" />
        <v-select label="Organisation" v-model="bm.organisation" :items="organisations" />
      <div class="d-flex">
        <v-select label="Role 1" v-model="role1" :items="roles" />
        <v-spacer />
        <v-checkbox label="Ad interim" v-model="adinterim1" />
      </div>
      <div class="d-flex">
        <v-select label="Role 2" v-model="role2" :items="roles" />
        <v-spacer />
        <v-checkbox label="Ad interim" v-model="adinterim2" />
      </div>
      <div class="d-flex">
        <v-select label="Role 3" v-model="role3" :items="roles" />
        <v-spacer />
        <v-checkbox label="Ad interim" v-model="adinterim3" />
      </div>
      <div class="d-flex">
        <v-select label="Role 4" v-model="role4" :items="roles" />
        <v-spacer />
        <v-checkbox label="Ad interim" v-model="adinterim4" />
      </div>
    </v-col>
    <v-col cols=12 sm=6>
      <v-checkbox label="Enabled" v-model="bm.enabled" />
      <v-text-field label="Priortity" type="number" v-model="bm.priority" />
      <v-checkbox label="Show email" v-model="bm.permissions.showemail" />
      <v-checkbox label="Show mobile" v-model="bm.permissions.showmobile" />
      <v-checkbox label="Show picture" v-model="bm.permissions.showpicture" />
    </v-col>
  </v-row>
      
</v-container>
</template>

<script>

import { mapState } from 'vuex'
import { bearertoken } from "@/util/token"
import { organisations } from "@/util/cms"


export default {

  name: "BoardMemberEdit",

  computed: {
    ...mapState(['token', 'api']),
  },

  data () {return {
    adinterim1: false,
    adinterim2: false,
    adinterim3: false,
    adinterim4: false,
    bm: {permissions:{}},
    organisations: organisations,
    roles: [],
    role1: '',
    role2: '',
    role3: '',
    role4: '',
  }},

  methods: {

    back () {
      this.$router.push('/mgmt/boardmember/list');
    },

    getBoardMember() {
      let self=this;
      this.api.getBoardMember(
        {id: this.$route.params.id},
        {securities: bearertoken(this.token)},
      ).then(
        function(data) {
          self.readBoardMember(data.obj);
        },
        function(data){
          console.error('failed get boardmember', data)
          self.$root.$emit('snackbar', {text: 'Getting boardmember failed', reason: data})          
        }
      );
    },

    getBoardRoles() {
      let self=this;
      this.api.getBoardRoles({},
        {securities: bearertoken(this.token)},
      ).then(
        function(data) {
          self.roles = data.obj.roles.map(r => r.name).sort();
        },
        function(rc){
          console.error('failed get roles', rc)
          // TODO snackbar
        }
      )
    },    

    readBoardMember (boardmember) {
      this.bm = boardmember;
      console.log('baordroles', boardmember.boardroles)
      if (boardmember.boardroles.length > 0) {
        this.role1 = boardmember.boardroles[0];
        this.adinterim1 = boardmember.adinterim[0];
      }
      if (boardmember.boardroles.length > 1) {
        this.role2 = boardmember.boardroles[1];
        this.adinterim2 = boardmember.adinterim[1];
      }
      if (boardmember.boardroles.length > 2) {
        this.role3 = boardmember.boardroles[2]
        this.adinterim3 = boardmember.adinterim[2]
      }
      if (boardmember.boardroles.length > 3) {
        this.role4 = boardmember.boardroles[3]
        this.adinterim4 = boardmember.adinterim[3]
      }
    },

    remove () {
      let self=this;
      if (window.confirm('Are you sure to delete boardmember "' + this.first_name + 
          ' ' + this.last_name + '"?')) {
        this.api.delete_boardmember(
          { id: this.$route.params.id },
          {securities: bearertoken(this.token)},
        ).then(
          function(){
            // TODO show deleted
            console.log('successfully deleted boardmember')
            self.back();
          }, 
          function(data){
            // TODO show error message
            console.error('failed to delete', data);
          }
        );
      }
    },

    save () {
      let self=this, roles=[], adinterim=[] ;
      const {id, ...boardmember} = this.bm;
      if (this.role1.length) {
        roles.push(this.role1);
        adinterim.push(this.adinterim1);
      }
      if (this.role2.length) {
        roles.push(this.role2)
        adinterim.push(this.adinterim2);
      }
      if (this.role3.length) {
        roles.push(this.role3)
        adinterim.push(this.adinterim3);
      }
      if (this.role4.length) {
        roles.push(this.role4)
        adinterim.push(this.adinterim4);
      }
      boardmember.boardroles = roles;
      boardmember.adinterim = adinterim;
      this.api.updateBoardMember({id},{
        requestBody: boardmember,
        securities: bearertoken(this.token),        
      }).then(
        function(){
          // TODO successfully saved
          console.log('successfully saved board member')
          self.$root.$emit('snackbar', {text: 'Board member saved'})          
        },
        function(data){
          // TODO show error message
          console.error('failed to save', data);
          self.$root.$emit('snackbar', {text: 'Saving board member failed', reason: data})          
          self.back();
        }
      );
    },

  },

  mounted () {
    this.getBoardMember();
    this.getBoardRoles();
  }

}
</script>

<style scoped>
.bordermd {
  border: 1px solid grey;
}
</style>
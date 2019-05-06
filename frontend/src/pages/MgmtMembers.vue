<template>
  <v-container fluid>

    <mgmt-members-list @update="update($event)" v-show="section == 'list'" 
      :selection="selection"  :ts="ts" />
    <mgmt-members-edit @update="update($event)" v-if="section == 'edit'"
      :member="member" :ts="ts" :groupdefs="groupdefs"  :roledefs="roledefs" />
    <mgmt-members-add @update="update($event)" v-if="section == 'add'"/>
    <mgmt-members-photo @update="update($event)" v-if="section == 'photo'"
      :member="member"  :ts="ts" />
    <mgmt-members-groups @update="update($event)" v-if="section == 'groups'" 
       :groupdefs="groupdefs"  :roledefs="roledefs"/>
    <v-snackbar v-model="snackbar" :timeout="timeout" bottom>
      {{ snacktext }}
      <v-btn flat @click="snackbar = false">
        <v-icon>cancel</v-icon>
      </v-btn>
    </v-snackbar>
  </v-container>
</template>

<script>

import api from '../util/api'


import MgmtMembersList from '../components/MgmtMembersList'
import MgmtMembersEdit from '../components/MgmtMembersEdit'
import MgmtMembersAdd from '../components/MgmtMembersAdd'
import MgmtMembersPhoto from '../components/MgmtMembersPhoto'
import MgmtMembersGroups from '../components/MgmtMembersGroups'

export default {
  name: "MgmtMembers",

  data () {return {
    groupdefs: [],
    member: {},
    roledefs: [],
    section: 'list',
    selection: [],
    snackbar: false,
    snacktext: '',
    ts: new Date(),
    timeout: 4000,
  }},

  components: {
    MgmtMembersList,
    MgmtMembersEdit,
    MgmtMembersAdd,
    MgmtMembersPhoto,
    MgmtMembersGroups,
  },

  methods: {
    update (e) {
      console.log('update', e);
      if (e.section)
        this.section = e.section;
      if (e.member)
        this.member = e.member;
      if (e.selection)
        this.selection = e.selection
      if (e.reload) 
        this.ts = new Date();
      if (e.text) {
        this.snacktext = e.text;
        this.snackbar = true;
      }
      if (e.groupdefs)
        this.groupdefs = e.groupdefs;
      if (e.roledefs)
        this.roledefs = e.roledefs;
    }
  },

  mounted () {
    api('getGroupRoles', {}).then(
      function(data){
        this.groupdefs = data.groupnames;
        this.roledefs = data.rolenames;
      }.bind(this), 
      function(data){
        console.error('Could not get Group Roles', data)
      }
    );
  }
}
</script>

<style scoped>

</style>
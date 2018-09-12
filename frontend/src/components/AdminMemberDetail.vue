<template>
<div >
  <h3>Add a new member</h3>
  <h3>Edit a member</h3>
  <v-text-field label="First name" v-model="mbr.first_name">
  </v-text-field>
  <v-text-field label="Last name" v-model="mbr.last_name">
  </v-text-field>
  <v-text-field label="Email" v-model="mbr.email">
  </v-text-field>
  <v-text-field label="Mobile" v-model="mbr.mobile">
  </v-text-field>
  <v-text-field label="Id national" v-model="mbr.idbel">
  </v-text-field>
  <v-text-field label="org1" v-model="mbr.org[0].group">
  </v-text-field>
  <v-text-field label="role1" v-model="mbr.org[0].role">
  </v-text-field>
  <v-text-field label="org2" v-model="mbr.org[1].group">
  </v-text-field>
  <v-text-field label="role2" v-model="mbr.org[1].role">
  </v-text-field>
  <v-text-field label="org3" v-model="mbr.org[2].group">
  </v-text-field>
  <v-text-field label="role3" v-model="mbr.org[2].role">
  </v-text-field>
  <div>
    <v-btn @click="save" class="green white--text">
      Save
    </v-btn>
  </div>

</div>

</template>

<script>
import api from '../api/api';

export default {
  name: "AdminMembersList",
  props: ['mbr'],
  methods: {
    save () {
      var self = this;
      api(this.mode == 'add' ? 'addMember' : 'putmember', this.mbr).then(
        function(data){
          self.$emit('updatembr', 'list')
        },
        function(data) {
          console.error('adding mbr failed', data)
        }
      )

    },
  }

}
</script>

<style scoped>

</style>
<template>
<div >
  <h3 v-show="mode == 'edit'">Photo</h3>
  <div>
    <v-btn @click="save" class="green white--text">
      Save
    </v-btn>
  </div>

</div>

</template>

<script>
import api from '../api/api';
import Croppie from 'croppie';

export default {
  name: "AdminMembersList",
  props: ['mbr', 'mode'],
  methods: {
    save () {
      var self = this;
      var idbel = this.mbr.oldidbel;
      delete this.mbr.oldidbel;
      api(this.mode == 'add' ? 'addMember' : 'saveMember', {
          idbel: idbel,
          member: this.mbr,
      }).then(
        function(data){
          self.$emit('updatembr', 'list')
        },
        function(data) {
          this.mbr.oldibel = idbel;
          console.error('adding mbr failed', data)
        }
      )
    },
  }

}
</script>

<style scoped>

</style>
<template>
<div>
  <h2>Existing Members</h2>
  <div>
    <v-btn @click="add" class="green white--text">
      Add Member
    </v-btn>
  </div>
  <v-layout v-for="(m,ix) in mbrs" :key="m.idbel" class="my-1">
    <v-flex xs1 v-text="ix+1"></v-flex>
    <v-flex xs6 v-text="fullname(m)"></v-flex>
    <v-flex xs5>
      <v-btn small flat icon class="green" @click.stop="edit(m)">
        <v-icon color="white">edit</v-icon>
      </v-btn>
      <v-btn small flat icon class="green">
        <v-icon color="white">photo</v-icon></v-btn>
    </v-flex>
  </v-layout>

</div>

</template>

<script>
import api from '../api/api';

export default {
  name: "AdminMembersList",
  props: ['mbrs'],
  methods: {
    add () {
      this.$emit('updatembr', 'add');
    },
    edit (m) {
      this.$emit('updatembr', 'edit', m)
    },
    fullname (m) {
      return m.first_name + ' ' + m.last_name;
    },
    photo (m) {
      this.$emit('updatembr', 'photo', m)
    },
  }

}
</script>

<style scoped>

</style>
<template>
<v-container fluid grid-list-md class="elevation-1">
  <v-layout row wrap>
    <v-flex>
        <h1>New Participant </h1>
    </v-flex>
    <v-flex>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="back()" slot="activator">
          <v-icon>arrow_back</v-icon>
        </v-btn>
        <span>Go Back</span>
      </v-tooltip>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="save()" slot="activator">
          <v-icon>save</v-icon>
        </v-btn>
        <span>Save changes</span>
      </v-tooltip>
    </v-flex>
  </v-layout>
  <v-layout row wrap>
    <v-flex sm6 xs12>
      <v-text-field label="Last name" v-model="p.last_name" />
      <v-text-field label="First name" v-model="p.first_name" />
      <v-text-field label="ID BEL" v-model="p.idbel" /> 
      <v-select label="Locale" v-model="p.locale" :items="locales"/>
    </v-flex>
    <v-flex sm6 xs12>
      <v-select label="Gender" v-model="p.gender" :items="genders" />
      <v-text-field label="Email address" v-model="p.emailplayer" />
      <v-text-field label="Mobile number" v-model="p.mobileplayer" />
    </v-flex>
  </v-layout>

</v-container>
</template>

<script>

import api from '../util/api'

export default {
  name: "MgmtMembersAdd",

  data () {return {
    genders: [
      {value: 'M', text: 'Male'},
      {value:'F', text: 'Female'},
    ],
    locales: ['nl', 'fr', 'de', 'en'],
    p: {},
  }},

  methods: {

    back () {
      this.$emit('update', {section: 'list', params:{}})
    },

    save () {
      api('addMember', {
        member: this.p,
      }).then(
        function(data){
          this.$emit('update', { 
            section: 'list', 
            reload: true,
            text: 'New member saved.'
          })
        }.bind(this),
        function(data){
          console.error('failed to save', data);
        }
      );
    },
  },


}
</script>

<style scoped>

</style>
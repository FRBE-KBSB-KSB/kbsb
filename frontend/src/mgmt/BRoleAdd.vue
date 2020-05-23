<template>
<v-container class="elevation-2">
  <v-row>
    <v-col cols=9>
      <h1>New member</h1>
    </v-col>
    <v-col cols=3>
      <v-tooltip bottom>
          <template v-slot:activator="{ on }">
            <v-btn v-on="on" @click="back()" fab outlined 
                  color="deep-purple">
              <v-icon>arrow_back</v-icon>
            </v-btn>
          </template>
          <span>Go Back</span>
      </v-tooltip>
      <v-tooltip bottom>
          <template v-slot:activator="{ on }">
            <v-btn v-on="on" @click="save()" fab outlined 
                  color="deep-purple">
              <v-icon>save</v-icon>
            </v-btn>
          </template>
          <span>Save changes</span>
      </v-tooltip>
    </v-col>
  </v-row>
  <v-row>
    <v-text-field label="Name role" v-model="name" />
  </v-row>
</v-container>
</template>

<script>

import { mapState } from 'vuex'

export default {
  
  name: "BRoleAdd",

  data () {return {
    name: '',
  }},

  computed: {
    ...mapState(['token', 'api'])
  },

  methods: {

    back () {
      this.$router.back();
    },

    save () {
      let self=this;
      this.api.create_board_role({}, {
        requestBody: {
          name: this.name
        }
      }).then(
        function(rc){
          self.$root.$emit('snackbar', {text: 'Boardrole created'})
          self.$router.push('/mgmt/brole/edit/' + rc.obj)
        },
        function(rc){
          console.error('failed to save', rc);
          // TODO snackbar added
        });
    },
  },

}
</script>

<style scoped>

</style>
<template>
<v-container grid-list-md class="elevation-1">
  <v-row>
    <v-col cols=9>
      <h1>New Board Role</h1>
    </v-col>
    <v-col cols=3>
      <v-tooltip bottom>
          <template v-slot:activator="{ on }">
            <v-btn v-on="on" @click="back()" fab outlined 
                  color="deep-purple">
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
          </template>
          <span>Go Back</span>
      </v-tooltip>
      <v-tooltip bottom>
          <template v-slot:activator="{ on }">
            <v-btn v-on="on" @click="save()" fab outlined 
                  color="deep-purple">
              <v-icon>mdi-content-save</v-icon>
            </v-btn>
          </template>
          <span>Save changes</span>
      </v-tooltip>
    </v-col>
  </v-row>
  <v-card>
    <v-card-text>
      <v-text-field label="Name" v-model="name" />
    </v-card-text>
  </v-card>

</v-container>
</template>

<script>

import { mapState } from 'vuex'
import { bearertoken } from "@/util/token"

export default {
  
  name: "BoardRoleAdd",

  data () {return {
    content: '',
    br: {},
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
      this.api.createBoardRole({}, {
        requestBody: {
          'name': this.name,
        },
        securities: bearertoken(this.token),
      }).then(
        function(data){
          console.log('board role  created', data)
          self.$router.push('/mgmt/boardrole/edit/'  + data.body)
          self.$root.$emit('snackbar', {text: 'Board role created'})          
        },
        function(data){
          console.error('failed to save', data);
          self.$root.$emit('snackbar', {text: 'Board role not created'})          
        }
      );
    },
  },


}
</script>

<style>

.dropbox {
  width: 100%;
  height: 100px;
}

</style>
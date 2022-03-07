<template>
<v-container grid-list-md class="elevation-1">
  <v-row>
    <v-col cols=9>
      <h1>New Board Member</h1>
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
      <v-text-field label="First name" v-model="first_name" />
      <v-text-field label="Last name" v-model="last_name" />
      <v-text-field label="E-mail" v-model="email" />
      <v-text-field label="Mobile" v-model="mobile" />
      <v-select label="Organisation" v-model="organisation" :items="organisations" />
    </v-card-text>
  </v-card>

</v-container>
</template>

<script>

import { mapState } from 'vuex'
import { bearertoken } from "@/util/token"
import { organisations } from "@/util/cms"

export default {
  
  name: "BoardMemberAdd",

  data () {return {
    bm: {},
    first_name: '',
    last_name: '',
    email: '',
    mobile: '',
    organisation: '',
    organisations: organisations, 
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
      this.api.createBoardMember({}, {
        requestBody: {
          first_name: this.first_name,
          last_name: this.last_name,
          email: this.email,
          mobile: this.mobile,
          organisation: this.organisation,
        },
        securities: bearertoken(this.token),
      }).then(
        function(data){
          console.log('board member  created', data)
          self.$router.push('/mgmt/boardmember/edit/'  + data.body)
          self.$root.$emit('snackbar', {text: 'Board member created'})          
        },
        function(data){
          console.error('failed to save', data);
          self.$root.$emit('snackbar', {text: 'Board member not created'})          
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
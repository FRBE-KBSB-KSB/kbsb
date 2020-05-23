<template>
<v-container class="elevation-2">
  <v-row>
    <v-col cols=12 sm=8>
        <h1>Edit board member: {{ member.first_name }} {{ member.last_name }} </h1>
    </v-col>
    <v-col col=12 sm=4>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" outlined fab color="deep-purple" @click="back()" 
              slot="activator">
            <v-icon>arrow_back</v-icon>
          </v-btn>
        </template>
        <span>Go Back</span>
      </v-tooltip>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" outlined fab color="deep-purple" @click="remove()" 
              slot="activator">
            <v-icon>delete</v-icon>
          </v-btn>
        </template>
        <span>Delete BMember</span>
      </v-tooltip>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" outlined fab color="deep-purple" @click="save()" 
              slot="activator">
            <v-icon>save</v-icon>
          </v-btn>
        </template>
        <span>Save BMember</span>
      </v-tooltip>
    </v-col>
  </v-row>
  <v-row>
    <v-col cols=12 sm=6>
      <v-text-field label="First name" v-model="first_name" />
      <v-text-field label="Last name" v-model="last_name" />
      <v-text-field label="Active" v-model="active" />
    </v-col>
    <v-col cols=12 sm=6>
      <v-text-field label="E-mail" v-model="email" />
      <v-text-field label="Mobile" v-model="mobile" />
      <v-text-field label="Priority" v-model="priority" />
    </v-col>
  </v-row>

</v-container>
</template>

<script>

import { mapState } from 'vuex'

export default {

  name: "PageEdit",

  computed: {
    ...mapState(['token', 'api']),
  },

  data () {return {
    first_name: '',
    last_name: '',
    active: true,
    email: '',
    mobile: '',
    priority: 10,
    member: {},
  }},

  methods: {

    back () {
      this.$router.back();
    },

    fetchMember() {
      let self=this;
      this.api.get_board_member({
        id: this.$route.params.id
      }).then(
        function(rc) {
          self.readBMember(rc.obj.member)
        },
        function(rc){
          console.error('failed get bmember', rc)
          // TODO snackbar
        }
      )
    },

    readBMember (member) {
      this.member = member;
      this.first_name = member.first_name + '';
      this.last_name = member.last_name + '';
      this.active = !!member.active;
      this.email = member.email + '';
      this.mobile = member.mobile + '';
      this.priority = member.priority + 0;
    },


    remove () {
      let self=this;
      if (window.confirm('Are you sure to delete ' + this.fullname)) {
        this.api.delete_board_member({
          id: this.role.id
        }).then(
          function(){
            self.$router.push('/mgmt/bmember/list')
            self.$root.$emit('snackbar', {text: 'Boardmember deleted'})
          }, 
          function(rc){
            console.error('failed to delete', rc);
            // TODO snackbar
          })
      }

    },

    save () {
      let self = this;
      this.api.update_board_role({id: this.member.id}, {
        requestBody: {
          first_name: this.first_name,
          last_name: this.last_name,
          active: this.active,
          email: this.email,
          mobile: this.mobile,
          priority: this.priority
        }
      }).then(
        function(){
          self.$router.push('/mgmt/bmember/list')
          self.$root.$emit('snackbar', {text: 'Boardmember saved'})
        },
        function(data){
          console.error('failed to save', data);
          // TODO snackbar
        }
      );
    },

  },

  mounted () {
    // make sure the api is loaded
    if (this.api) this.fetchMember()
  },
  
  watch: {
    api: function() {
      this.fetchMember()
    }
  },

}
</script>

<style scoped>
.bordermd {
  border: 1px solid grey;
}
</style>
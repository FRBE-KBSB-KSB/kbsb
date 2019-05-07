<template>
<v-container fluid grid-list-md class="elevation-1">
  <v-layout row wrap>
    <v-flex>
        <h1>Edit Member: {{ fullname }} </h1>
    </v-flex>
    <v-flex>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="back()" slot="activator">
          <v-icon>arrow_back</v-icon>
        </v-btn>
        <span>Go Back</span>
      </v-tooltip>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="removeMember()" slot="activator">
          <v-icon>delete</v-icon>
        </v-btn>
        <span>Delete member</span>
      </v-tooltip>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="saveMember()" slot="activator">
          <v-icon>save</v-icon>
        </v-btn>
        <span>Save changes</span>
      </v-tooltip>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="gotoPhoto()" slot="activator">
          <v-icon>face</v-icon>
        </v-btn>
        <span>Edit photo</span>
      </v-tooltip>
    </v-flex>
  </v-layout>
  <v-layout row wrap>
    <v-flex sm6 xs12>
      <v-text-field label="Last name" v-model="p.last_name" />
      <v-text-field label="First name" v-model="p.first_name" />
      <v-select label="Chess title" v-model="p.chesstitle"
                :items="['', 'GM', 'IM', 'FM', 'WGM', 'WIM', 'WFM', 'IA', 'FA']"
      />
      <v-menu :close-on-content-click="false" v-model="menu_birthdate"
        :nudge-right="40" lazy transition="scale-transition" offset-y
        full-width min-width="290px">
        <v-text-field slot="activator" v-model="p.birthdate"
          label="Birthdate" prepend-icon="event" readonly
        ></v-text-field>
        <v-date-picker v-model="p.birthdate" @input="menu_birthdate = false"
                       color="green" />
      </v-menu>
      <v-select label="Gender" v-model="p.gender" :items="genders" />
      <v-text-field label="ID Bel" v-model="p.idbel" />
      <v-text-field label="ID Fide" v-model="p.idfide" />
    </v-flex>
    <v-flex sm6 xs12>
      <v-text-field label="Email player" v-model="p.email" />
      <v-text-field label="Mobile player" v-model="p.mobiletel" />
      <v-checkbox label="Show e-mail publicly" v-model="privacy.email" />
      <v-checkbox label="Show mobile publicly" v-model="privacy.mobiletel" />
      <v-text-field label="Federation" v-model="p.federation" />
      <v-textarea label="Remarks" v-model="p.remarks" />
    </v-flex>
    <v-flex xs12>
      <h4>Roles</h4>
      <v-layout row wrap>
        <v-flex sm10 class="elevation-2 grey lighten-4 pa-1 ma-1" >
          <v-layout row wrap v-for="(r, ix) in roles" :key="ix" class="">
            <v-flex sm4 >
              <v-select label="Group" v-model="r.groupname" @change="setupRoles()"
                    :items="groupdefs" item-text="name" item-value="shortname"
              />
            </v-flex>
            <v-flex sm7>
              <v-select label="Role" v-model="r.rolename" @change="setupRoles()"
                        :items="roledefs"  item-text="name" item-value="shortname"
              />
            </v-flex>
            <v-flex sm1>
              <v-icon @click="removeRole(ix)">remove_circle</v-icon>
            </v-flex>
          </v-layout>
        </v-flex>
      </v-layout>
    </v-flex>
  </v-layout>

</v-container>
</template>

<script>

import api from '../util/api'
import DateFormatted from "./DateFormatted";

export default {
  name: "MgmtMembersEdit",

  components: {
    DateFormatted,
  },

  props: ['member', 'groupdefs', 'roledefs'],

  computed :  {
    fullname () {
      return this.p.first_name + ' ' + this.p.last_name;
    }
  },

  data () {return {
    genders: [
      {value: 'M', text: 'Male'},
      {value:'F', text: 'Female'},
    ],
    locales: ['nl', 'fr', 'de', 'en'],
    menu_birthdate: false,
    p: {},
    privacy: {},
    roles: [],
  }},

  methods: {

    back () {
      this.$emit('update', {section: 'list'})
    },

    gotoPhoto () {
      this.$emit('update', {section: 'photo', member: this.member})
    },

    removeMember () {
      if (window.confirm('Are you sure to delete ' + this.fullname)) {
        api('deleteMember', {
          id: this.member.id
        }).then(function(){
          this.$emit('update', {section: 'list', reload: true,
            text: this.fullname + ' deleted.'})
        }.bind(this), function(data){
          console.error('failed to delete', data);
        })
      }
    },

    removeRole(ix) {
      this.roles.splice(ix, 1);
    },

    setupRoles(ro) {
      let roles = [];
      ro = ro || this.roles;
      console.log('change', ro, ro.length)
      ro.forEach(function(r){
        console.log('r', r.groupname, r.rolename);
        if (r.groupname || r.rolename)
          roles.push(r)
      })
      console.log('roles', roles, roles.length)
      roles.push({groupname: '', rolename: ''})
      this.roles = roles;
    },

    saveMember () {
      let roles = [];
      this.roles.forEach(function(r){
        if (r.groupname && r.rolename)
          roles.push(r);
      })
      this.p.roles = roles;
      api('updateMember', {
        id: this.member.id,
        member: this.p,
      }).then(
        function(){
          this.$emit('update', {section: 'edit', reload: true,
            text: this.fullname + ' saved.'})
        }.bind(this),
        function(data){
          console.error('failed to save', data);
        }
      );
    },

  },

  mounted () {
    api('getMember', {
      id: this.member.id
    }).then(
     function(data) {
        this.p = data.member;
        this.privacy = data.member.privacy;
        this.setupRoles(data.member.roles)
      }.bind(this)
    )
  }

}
</script>

<style scoped>

</style>
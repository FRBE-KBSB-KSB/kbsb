<template>
<v-container fluid grid-list-md class="elevation-1">
  <v-layout row wrap>
    <v-flex>
        <h1>Group Names</h1>
    </v-flex>
    <v-flex>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="back()" slot="activator">
          <v-icon>arrow_back</v-icon>
        </v-btn>
        <span>Go Back</span>
      </v-tooltip>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="saveGroupRole()" slot="activator">
          <v-icon>save</v-icon>
        </v-btn>
        <span>Save changes</span>
      </v-tooltip>
    </v-flex>
  </v-layout>
  <div v-for="(gr,ix) in groupnames" :key="ix">
    <v-layout row wrap >
      <v-flex sm4>
        <v-text-field label="Short name" v-model="gr.shortname" hide-details single-line
          @change="setupGroupNames()"  class=nopadding />
      </v-flex>    
      <v-flex sm6>
        <v-text-field label="Long name" v-model="gr.name" hide-details single-line 
          @change="setupGroupNames()" class=nopadding />
      </v-flex>
      <v-flex sm2>
        <v-icon v-show="ix != openedgroup"  @click="openGroupTranslations(ix)"
          >arrow_drop_down</v-icon>
        <v-icon v-show="ix == openedgroup" @click="openedgroup = -1"
          >arrow_drop_up</v-icon>
      </v-flex>
    </v-layout>
    <v-layout row v-show="ix == openedgroup">
      <v-flex sm10 class="elevation-2 grey lighten-4 ma-1 pa-1">
        <v-layout row>
          <v-flex sm1>nl</v-flex>    
          <v-flex sm4>
            <v-text-field label="Short name" v-model="gr.translations.nl_shortname" 
              hide-details single-line class=nopadding />
          </v-flex>
          <v-flex sm6>
            <v-text-field label="Long name" v-model="gr.translations.nl_name" 
              hide-details single-line class=nopadding />
          </v-flex>
        </v-layout>
        <v-layout row>
          <v-flex sm1>fr</v-flex>    
          <v-flex sm4>
            <v-text-field label="Short name" v-model="gr.translations.fr_shortname" 
              hide-details single-line class=nopadding />
          </v-flex>
          <v-flex sm6>
            <v-text-field label="Long name" v-model="gr.translations.fr_name" 
              hide-details single-line class=nopadding />
          </v-flex>
        </v-layout>
        <v-layout row >
          <v-flex sm1>de</v-flex>    
          <v-flex sm4>
            <v-text-field label="Short name" v-model="gr.translations.de_shortname" 
              hide-details single-line class=nopadding />
          </v-flex>
          <v-flex sm6>
            <v-text-field label="Long name" v-model="gr.translations.de_name" 
              hide-details single-line class=nopadding />
          </v-flex>
        </v-layout>
        <v-layout row>
          <v-flex sm1>en</v-flex>    
          <v-flex sm4>
            <v-text-field label="Short name" v-model="gr.translations.en_shortname" 
              hide-details single-line class=nopadding />
          </v-flex>
          <v-flex sm6>
            <v-text-field label="Long name" v-model="gr.translations.en_name" 
              hide-details single-line class=nopadding />
          </v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
  </div>

  <h1 class="mt-2">Role Names</h1>
  <div v-for="(rl,ix) in rolenames" :key="ix">
    <v-layout row wrap >
      <v-flex sm4>
        <v-text-field label="Short name" v-model="rl.shortname" hide-details single-line
          @change="setupRoleNames()"  class=nopadding />
      </v-flex>    
      <v-flex sm6>
        <v-text-field label="Long name" v-model="rl.name" hide-details single-line 
          @change="setupRoleNames()" class=nopadding />
      </v-flex>
      <v-flex sm2>
        <v-icon v-show="ix != openedrole"  @click="openRoleTranslations(ix)"
          >arrow_drop_down</v-icon>
        <v-icon v-show="ix == openedrole" @click="openedrole = -1"
          >arrow_drop_up</v-icon>
      </v-flex>
    </v-layout>
    <v-layout  v-show="ix == openedrole">
      <v-flex sm10 class="elevation-2 grey lighten-4 pa-1 ma-1" >
        <v-layout row>
          <v-flex sm1>nl</v-flex>    
          <v-flex sm4>
            <v-text-field label="Short name" v-model="rl.translations.nl_shortname" 
              hide-details single-line class=nopadding />
          </v-flex>
          <v-flex sm6>
            <v-text-field label="Long name" v-model="rl.translations.nl_name" 
              hide-details single-line class=nopadding />
          </v-flex>
        </v-layout>
        <v-layout row>
          <v-flex sm1>fr</v-flex>    
          <v-flex sm4>
            <v-text-field label="Short name" v-model="rl.translations.fr_shortname" 
              hide-details single-line class=nopadding />
          </v-flex>
          <v-flex sm6>
            <v-text-field label="Long name" v-model="rl.translations.fr_name" 
              hide-details single-line class=nopadding />
          </v-flex>
        </v-layout>
        <v-layout row >
          <v-flex sm1>de</v-flex>    
          <v-flex sm4>
            <v-text-field label="Short name" v-model="rl.translations.de_shortname" 
              hide-details single-line class=nopadding />
          </v-flex>
          <v-flex sm6>
            <v-text-field label="Long name" v-model="rl.translations.de_name" 
              hide-details single-line class=nopadding />
          </v-flex>
        </v-layout>
        <v-layout row>
          <v-flex sm1>en</v-flex>    
          <v-flex sm4>
            <v-text-field label="Short name" v-model="rl.translations.en_shortname" 
              hide-details single-line class=nopadding />
          </v-flex>
          <v-flex sm6>
            <v-text-field label="Long name" v-model="rl.translations.en_name" 
              hide-details single-line class=nopadding />
          </v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
  </div>

</v-container>
</template>

<script>

import api from '../util/api'
import DateFormatted from "./DateFormatted";

export default {
  name: "MgmtMembersGroups",

  components: {
    DateFormatted,
  },

  props: ['member', 'groupdefs', 'roledefs'],

  data () {return {
    groupnames: [],
    rolenames: [],
    openedgroup: -1,
    openedrole: -1,
  }},

  methods: {

    back () {
      this.$emit('update', {section: 'list'})
    },

    openGroupTranslations(ix) {
      this.openedgroup = ix;
    },

    openRoleTranslations(ix) {
      this.openedrole = ix;
    },

    setupGroupNames(gr) {
      let groupnames = [];
      gr = gr || this.groupnames;
      gr.forEach(function(g){
        if (g.shortname || g.name)
          groupnames.push(g)
      }.bind(this))
      groupnames.push({shortname: '', name: '', translations:{}})
      this.groupnames = groupnames;
    },

    setupRoleNames(rl) {
      let rolenames = [];
      rl = rl || this.rolenames;
      rl.forEach(function(r){
        if (r.shortname || r.name)
          rolenames.push(r)
      }.bind(this))
      rolenames.push({shortname: '', name: '', translations: {}})
      this.rolenames = rolenames;
    },

    saveGroupRole () {
      let grps = [], rls = [];
      this.groupnames.forEach(function(g){
        if (g.shortname && g.name)
          grps.push(g)
      })
      this.rolenames.forEach(function(r){
        if (r.shortname && r.name)
          rls.push(r)
      })
      api('updateGroupRoles', {
        groupnames: grps,
        rolenames: rls
      }).then(
        function(){
          this.$emit('update', {section: 'list', reload: true, roledefs: rls,
            text: 'Groups and roles saved.', groupdefs: grps })
        }.bind(this),
        function(data){
          console.error('failed to save', data);
        }
      );
    },
  },

  mounted () {
    this.setupGroupNames(this.groupdefs);
    this.setupRoleNames(this.roledefs);
  }

}
</script>

<style scoped>

.nopadding {
  padding-top: 0;
}
</style>
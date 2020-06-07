<template>

  <v-container class="mt-1">
    <h1>
      <i18n-text 
        nl="Bestuur" 
        fr="Conseil d'administration" 
        de="Vorstand" 
        en="Board" />
    </h1>
    <h2>
      <i18n-text 
        nl="Bestuursleden" 
        fr="Membres du conseil d'administration" 
        de="Vorstandsmitglieder" 
        en="Board members" />
    </h2>
        
    <v-row >
      <v-col cols=12 md=6 xl=4 v-for="bm in board" :key="bm.id">
        <div class="ma-1 elevation-3 d-flex pa-1">

          <div class="flex-shrink-0 flex-grow-0">
            <img :src="bm.urlpicture" class="person-photo d-none d-lg-flex">
            <img :src="bm.urlpicture" class="person-photo-sm d-lg-none ">
          </div>
          <div class="d-flex flex-column flex-grow-1 ml-1">
            <div class="green lighten-3 pa-3">
              {{bm.first_name}} {{bm.last_name}}
            </div>
            <div class="pa-3">
              <div v-for="r in bm.boardroles" :key="r.name">{{i18nroles[r]}}</div>
              <div>{{bm.mobile}}</div>
              <div>{{bm.email}}</div>
            </div>
            <div class="pa-3 d-flex">
              <v-btn text icon class="green mx-2" :href="'tel:' + bm.mobile">
                  <v-icon color="white">mdi-phone</v-icon>
              </v-btn>
              <v-btn text icon class="green mx-2" :href="'sms:' + bm.mobile">
                  <v-icon  color="white">mdi-message-processing</v-icon>
              </v-btn>
              <v-btn text icon  class="green mx-2" :href="'mailto:' + bm.email ">
                  <v-icon color="white">mdi-email</v-icon>
              </v-btn>
            </div>          
          </div>
        </div>

      </v-col>  
    </v-row>

    <h2>
      <i18n-text 
        nl="Gemandateerden" 
        fr="Personnes mandatées" 
        de="Mandierte Personen" 
        en="Mandated persons" />
    </h2>

    <v-row >
      <v-col cols=12 md=6 xl=4 v-for="bm in mandated" :key="bm.id">
        <div class="ma-1 elevation-3 d-flex pa-1">

          <div class="flex-shrink-0 flex-grow-0">
            <img :src="bm.urlpicture" class="person-photo d-none d-lg-flex">
            <img :src="bm.urlpicture" class="person-photo-sm d-lg-none ">
          </div>
          <div class="d-flex flex-column flex-grow-1 ml-1">
            <div class="green lighten-3 pa-3">
              {{bm.first_name}} {{bm.last_name}}
            </div>
            <div class="pa-3">
              <div v-for="r in bm.boardroles" :key="r.name">{{i18nroles[r]}}</div>
              <div>{{bm.mobile}}</div>
              <div>{{bm.email}}</div>
            </div>
            <div class="pa-3 d-flex">
              <v-btn text icon class="green mx-2" :href="'tel:' + bm.mobile">
                  <v-icon color="white">mdi-phone</v-icon>
              </v-btn>
              <v-btn text icon class="green mx-2" :href="'sms:' + bm.mobile">
                  <v-icon  color="white">mdi-message-processing</v-icon>
              </v-btn>
              <v-btn text icon  class="green mx-2" :href="'mailto:' + bm.email ">
                  <v-icon color="white">mdi-email</v-icon>
              </v-btn>
            </div>          
          </div>
        </div>
      </v-col>  
    </v-row>

  </v-container>

</template>

<script>

import I18nText from "@/components/I18nText"
import {mapState} from "vuex"
import { pictureurl } from '@/util/cms'

export default {

  name: 'BoardListing',

  components: {
    I18nText,
  },

  data () {return {
    board: [],
    mandated: [],
    i18nroles: {},  
  }},

  computed: {
    ...mapState(['locale', 'api'])
  },

  methods: {

    compareMembersByPriority(a,b) {
      return b.priority - a.priority
    },

    getBoardMembers() {
      let self=this;
      this.api.get_board_members().then(
        function(data) {
          self.readBoardMembers(data.obj.members);
        },
        function(data){
          console.error('getting getFiles', data);
          self.$root.$emit('snackbar', {text: 'Getting files failed', reason: data})            
        }
      );
    },

    getBoardRoles() {
      let self=this;
      this.api.get_board_roles().then(
        function(rc) {
          self.readBoardRoles(rc.obj.roles)
        },
        function(rc){
          console.error('failed get bmember', rc)
          // TODO snackbar
        }
      )
    },

    readBoardRoles(roles) {
      let self=this;
      this.i18nroles = {};
      roles.forEach(function(r){
        self.i18nroles[r.name] = r.i18n[self.locale];
      })
    },

    readBoardMembers(members){
      console.log('processing board members', members)
      let self=this;
      this.board=[];
      this.mandated=[];
      members.forEach(function(m){
        m.urlpicture = pictureurl + m.id;
        switch (m.membertype) {
          case 'board':
            self.board.push(m)
            break;
          case 'mandated person':
            self.mandated.push(m)
            break;
        }
      })
      this.board.sort(this.compareMembersByPriority)
    },
    
  },

  mounted () {
    this.getBoardMembers();
    this.getBoardRoles();
    console.log('Boardlisting loaded')
  },

}
</script>


<style scoped>

.person-photo {
  width: 160px;
}

.person-photo-sm {
  width: 120px;
}

</style>

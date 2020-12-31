<template>

<v-container>
  <h1>Management Clubs</h1>
  <h3>Lookup Up Club</h3>
  <v-row>
    <v-col cols=12 sm=6> 
      <v-text-field v-model="id_club" label="Club number"
        append-icon="mdi-magnify" @click:append="search" />
    </v-col>
  </v-row>

  <v-row v-if="club_found">
    <v-col cols=12 sm=6> 
      <h4>Details</h4>
      {{ club.long_name}}<br />
      {{ club.short_name}}<br />
      Federation: {{ federation }}
      <div  v-show="club.website">Website: 
        <a :href="club.website" target="_blank">{{ club.website}}</a>
      </div>
      <div v-show="club.email">E-mail address: 
        <a :href="'mailto:' + club.email">{{ club.email }}</a>
      </div>
      playing: {{ club.playdates }}
    </v-col>
    <v-col cols=12 sm=6> 
      <h4>Address</h4>
      {{ club.address_venue}}<br />
      {{ club.address_street}}<br />
      {{ club.address_postal_code}} {{ club.address_town}}
    </v-col>
    <v-col cols=12 sm=6> 
      <h4>Board</h4>
      president: {{club.id_president}}<br />
      vice president: {{club.id_vicepresident}}<br />
      secretary: {{club.id_secretary}}<br />
      tournament director: {{club.id_tournament}}<br />
      treasurer: {{club.id_treasurer}}<br />
      interclub responsible: {{club.id_interclub}}<br />
      youth responsible: {{club.id_youth}}
    </v-col>
    <v-col cols=12 sm=6> 
      <h4>Bank details</h4>
      Bank account name: {{club.bankaccount_name}}<br />
      Bank account number: {{club.bankaccount_iban}}<br />
      Bank account bic: {{club.bankaccount_bic}}
    </v-col>

  </v-row>   
</v-container>

</template>

<script>

import { mapState } from 'vuex'
import { bearertoken } from "@/util/token"
// import DateFormatted from "@/components/DateFormatted"


export default {

  name: 'Clubs',

  data () {return {
    club: {},
    club_found:  false,
    id_club: '',
  }},

  computed: {
    ...mapState(['token', 'api']),
    federation(){
      switch (this.club.federation) {
        case 'V': return 'VSF';
        case 'F': return 'FEFB';
        case 'D': return 'SVDB'
      }
      return ''
    } 
  },

  // components: {
  //   DateFormatted,
  // },

  methods: {

    search () {
      let self=this;
      this.api.getClub(
        {id: this.id_club},
        {securities: bearertoken(this.token)},
      ).then(
        function(data) {
            console.log('club found', data.obj)
            self.club_found =  true;
            self.club = data.obj;
        },
        function(data){
          if (data.status == 401) {
            self.$router.push('/mgmt/login')
          }
          if (data.status == 404) {
            self.$root.$emit('snackbar', {text: 'Club not found', reason: data})            
          }
          else {
            console.error('getting getClub', data);
            self.$root.$emit('snackbar', {text: 'Getting club failed', reason: data})            
          }
        }
      );

    },
    
  },


}
</script>

<template>

<v-container>
  <h1>Management Members</h1>
  <h3>Lookup Up Member</h3>
  <v-row>
    <v-col cols=12 sm=6> 
      <v-text-field v-model="id_member" label="Member id"
        append-icon="mdi-magnify" @click:append="search" />
    </v-col>
  </v-row>

  <v-row v-if="member_found">
    <v-col cols=12 sm=6> 
      <h4>Details</h4>
      {{ member.last_name}}, {{ member.first_name}}<br />
      Birth date: {{ member.birthday }}<br />
      Birth place: {{ member.birthplace }}<br />      
      Gender: {{ member.gender }}<br />      
      Nationality: {{ member.nationality }}<br />
      Junior/Senior: {{ member.junior }}
    </v-col>
    <v-col cols=12 sm=6> 
      <h4>Address</h4>
      {{ member.address_number}}, {{ member.address_street}}<br />
      {{ member.address_postal_code}}{{ box }} {{ member.address_town}}<br />
      {{ member.address_country }}
    </v-col>
    <v-col cols=12 sm=6> 
      <h4>Affiliation</h4>
      Initial affiliation: {{ member.affiliation_initial_date}}<br />
      Last affiliation year: {{ member.affiliation_year}}<br />
      Last affiliation date: {{ member.affiliation_date}}<br />
      Last affiliation payment date: {{ member.affiliation_payment_date}}<br />
    </v-col>    
    <v-col cols=12 sm=6> 
      <h4>Chess data</h4>
      ID: {{ member.id}}<br />
      Club: {{ member.id_club}}<br />
      Federation: {{ federation }}<br />
      FIDE ID: {{ member.id_fide}}<br />
      FIDE Nationality: {{ member.nationality_fide}}<br />
      G license: {{ licenseg}}
    </v-col>
    <v-col cols=12 sm=6> 
      <h4>Transfer</h4>
      Old club: {{ member.transfer_club_old }}<br />
      Old federation: {{ member.transfer_federation_old }}<br />
      New club: {{ member.transfer_club_new }}<br />
      Date: {{ member.transfer_date }}<br />
      Opposed: {{ opposed }}
    </v-col>    

  </v-row>   
</v-container>

</template>

<script>

import { mapState } from 'vuex'
import { bearertoken } from "@/util/token"
// import DateFormatted from "@/components/DateFormatted"


export default {

  name: 'Members',

  data () {return {
    member: {},
    member_found:  false,
    id_member: '',
  }},

  computed: {
    ...mapState(['token', 'api']),
    federation(){
      switch (this.member.federation) {
        case 'V': return 'VSF';
        case 'F': return 'FEFB';
        case 'D': return 'SVDB'
      }
      return ''
    },
    box() {
      return (this.member && this.member.address_box) ? 
        ' Box ' + this.member.address_box : '';
    },
    deceased() {
      return (this.member && this.member.deceased) ? 'Deceased': '' 
    },
    licenseg() {
      return (this.member && this.member.licence_g) ? 'Yes': 'No' 
    },
    opposed() {
      return (this.member && this.member.opposed) ? 'Yes': 'No' 
    },
  },

  // components: {
  //   DateFormatted,
  // },

  methods: {

    search () {
      let self=this;
      this.api.getMember(
        {id: this.id_member},
        {securities: bearertoken(this.token)},
      ).then(
        function(data) {
            console.log('member found', data.obj)
            self.member_found =  true;
            self.member = data.obj;
        },
        function(data){
          if (data.status == 401) {
            self.$router.push('/mgmt/login')
          }
          if (data.status == 404) {
            self.$root.$emit('snackbar', {text: 'Member not found', reason: data})            
          }
          else {
            console.error('getting getMember', data);
            self.$root.$emit('snackbar', {text: 'Getting member failed', reason: data})            
          }
        }
      );

    },
   
  },


}
</script>

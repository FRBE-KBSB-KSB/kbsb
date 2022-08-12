<template>
  <v-container>
    <p v-if="!club.idclub">Please select a club to view the enrollment</p>
    <div v-if="club.idclub">
      <h3 v-show="status_consulting">Consulting club details</h3>
      <h3 v-show="status_modifying">Modifying club details</h3>
      <v-container>
        <v-row v-show="status_consulting">
          <v-col cols="12" sm="6" lg="4">
            <h4>Club details</h4>
            <div>Long name: {{ club.name_long }}</div>
            <div>Short name: {{ club.name_short }}</div>
            <div>Federation: {{ club.federation }}</div>
            <div>Club Venue: {{ club.venue }}</div>
            <div>Website: {{ club.website }}</div>
          </v-col>
          <v-col cols="12" sm="6" lg="4">
            <h4>Contact</h4>
            <div>Main email address: {{ club.email_main }}</div>
            <div>Email address Interclub: {{ club.email_intercLub }}</div>
            <div>Email address administration: {{ club.email_admin }}</div>
            <div>Email address finance: {{ club.email_finance }}</div>
            <div>Postal address: {{ club.address }}</div>
          </v-col>
          <v-col cols="12" sm="6" lg="4">
            <h4>Board Members</h4>
            TO DO
          </v-col>
          <v-col cols="12" sm="6" lg="4">
            <h4>Bank details</h4>
            <div>Bank account name: {{ club.bankaccount_name }}</div>
            <div>Bank account IBAN: {{ club.bankaccount_iban }}</div>
            <div>Bank account BIC: {{ club.bankaccount_bic }}</div>
          </v-col>
        </v-row>
        <v-row v-show="status_consulting">
          <v-btn @click="modifyClub">Modify club</v-btn>
        </v-row>
        <v-row v-show="status_modifying">
          <v-col cols="12" sm="6" lg="4">
            <h4>Club details</h4>
            <v-text-field v-model="club.name_long" label="Long name" />
            <v-text-field v-model="club.name_short" label="Short name" />
            <div>Federation: {{ club.federation }}</div>
            <v-textarea v-model="club.venue" label="Venue" />
            <v-text-field v-model="club.website" label="Website" />
          </v-col>
          <v-col cols="12" sm="6" lg="4">
            <h4>Contact</h4>
            <v-text-field v-model="club.email_main" label="Main E-mail address" />
            <v-text-field v-model="club.email_intercub" label="E-mail Interclub" />
            <v-text-field v-model="club.email_admin" label="E-mail administration" />
            <v-text-field v-model="club.email_finance" label="E-mail finance" />
            <v-textarea v-model="club.address" label="Postal address" />
          </v-col>
          <v-col cols="12" sm="6" lg="4">
            <h4>Board Members</h4>
            TO DO
          </v-col>
          <v-col cols="12" sm="6" lg="4">
            <h4>Bank details</h4>
            <v-text-field v-model="club.bankacount_name" label="Name bank account" />
            <v-text-field v-model="club.bankaccount_iban" label="IBAN bank account" />
            <v-text-field v-model="club.bankaccount_bic" label="BIC bank account" />
          </v-col>
        </v-row>
        <v-row v-show="status_modifying">
          <v-btn @click="saveClub">Save club</v-btn>
          <v-btn @click="cancelClub">Cancel</v-btn>
        </v-row>
      </v-container>
    </div>
  </v-container>
</template>
<script>

const CLUB_STATUS = {
  CONSULTING: 0,
  MODIFYING: 1,
}
const empty_clubdetails = {
}

export default {

  name: 'Detail',

  data() {
    return {
      status: CLUB_STATUS.CONSULTING,
      clubdetails: {},
    }
  },

  props: {
    club: Object
  },

  computed: {
    logintoken() { return this.$store.state.newlogin.value },
    status_consulting() { return this.status == CLUB_STATUS.CONSULTING },
    status_modifying() { return this.status == CLUB_STATUS.MODIFYING },
  },

  methods: {

    cancelClub() {
      this.status = CLUB_STATUS.CONSULTING
      this.get_clubdetails(this.club)
    },

    emitInterface() {
      this.$emit("interface", "get_clubdetails", this.get_clubdetails);
    },

    async get_clubdetails() {
      if (!this.club.id) {
        this.clubdetails = empty_clubdetails
        return
      }
      try {
        const reply = await this.$api.club.mgmt_get_club({
          id: this.club.id,
          token: this.logintoken
        })
        this.clubdetails = { ...reply.data }
      } catch (error) {
        const reply = error.reply
        if (reply.status === 401) {
          this.$router.push('/mgmt/login')
        }
        else {
          console.error('Getting club details failed', reply.data.detail)
          this.$root.$emit('snackbar', { text: 'Getting club details failed' })
        }
      }
    },

    modifyClub() {
      this.status = CLUB_STATUS.MODIFYING
    },

    async saveClub() {
      try {
        const reply = await this.$api.club.mgmt_update_club({
          ...this.clubdetails,
          token: this.logintoken,
        })
        this.status = CLUB_STATUS.CONSULTING
        this.$root.$emit('snackbar', { text: 'Club saved' })
      } catch (error) {
        const reply = error.response
        if (reply.status === 401) {
          this.gotoLogin()
        }
        else {
          console.error('Saving enrollment', reply.data.detail)
          this.$root.$emit('snackbar', { text: 'Saving enrollment' })
        }
      }
    },

  },

  mounted() {
    this.emitInterface();
    this.$nextTick(() => {
      this.get_clubdetails();
    })
  },

}
</script>
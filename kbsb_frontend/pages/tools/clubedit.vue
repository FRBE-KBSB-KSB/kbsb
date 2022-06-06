<template>
  <v-container>
    <v-row>
      <v-col cols="10">
        <h2>Edit Club {{ clb.number }}: {{ clb.last_name }} {{ clb.first_name }}</h2>
      </v-col>
      <v-col col="2"  
        <v-tooltip bottom>
          <template #activator="{ on }">
            <v-btn
              slot="activator"
              outlined
              fab
              color="green"
              v-on="on"
              @click="back"
            >
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
          </template>
        </v-tooltip>
        <v-tooltip>
          <template #activator="{ on }">
            <v-btn
              slot="activator"
              outlined
              fab
              color="green"
              v-on="on"
              @click="saveClub"
            >
              <v-icon>mdi-content-save</v-icon>
            </v-btn>
          </template>        
          <span>Save</span>
        </v-tooltip>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" sm="6" lg="4">
        <h4>Details</h4>
        <v-text-field v-model="clb.name_long" label="Long name" />
        <v-text-field v-model="clb.name_short" label="Short name" />
        <div>Federation: {{ clb.federation }}</div>
        <v-textarea v-model="clb.venue" label="Venue" />
        <v-text-field v-model="clb.website" label="Website" />
      </v-col>
      <v-col cols="12" sm="6" lg="4">
        <h4>Contact</h4>
        <v-text-field v-model="clb.email_main" label="Main E-mail address" />
        <v-text-field v-model="clb.email_intercub" label="E-mail Interclub" />
        <v-text-field v-model="clb.email_admin" label="E-mail administration" />
        <v-text-field v-model="clb.email_finance" label="E-mail finance" />
        <v-textarea v-model="clb.address" label="Postal address" />
      </v-col>
      <v-col cols="12" sm="6" lg="4">
        <h4>Board</h4>
        TODO
      </v-col>
      <v-col cols="12" sm="6" lg="4">
        <h4>Bank details</h4>
        <v-text-field v-model="clb.bankacount_name" label="Name bank account" />
        <v-text-field v-model="clb.bankaccount_iban" label="IBAN bank account" />
        <v-text-field v-model="clb.bankaccount_bic" label="BIC bank account" />
      </v-col>
      <v-col cols="12" sm="6" lg="4">
        <h4>Access to Club manager</h4>
      </v-col>
      <v-col cols="12" sm="6" lg="4">
        <h4>Access to Interclub manager</h4>
      </v-col>
      <v-col cols="12" sm="6" lg="4">
        <h4>Access to Interclub results (team captains)</h4>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>

export default {

  name: 'Clubedit',

  layout: 'default',

  data () {
    return {
      idclub: this.$route.query.id,
      clb: {}
    }
  },

  computed: {
    oldlogin () { return this.$store.state.oldlogin.value }
  },

  mounted () {
    this.$store.commit('oldlogin/startup')
    if (!this.oldlogin.length) {
      this.gotoLogin()
    }    
    this.getClub()
  },

  methods: {

    back () {
      this.$router.go(-1)
    },

    async getClub () {
      console.log('Trying getClub', this.$route.query.id, this.oldlogin)
      try {
        const reply = await this.$api.club.get_c_club({
          id: this.$route.query.id,
          token: this.oldlogin
        })
        console.log('reply', reply.data)
        this.clb = {...reply.data}
      } catch (error) {
        const reply = error.replyonse
        console.error('getting get_c_club', reply)
        if (reply.status === 401) {
          this.$router.push('/mgmt/login')
        } else {
          this.$root.$emit('snackbar', { text: 'Getting club failed', reason: reply.data.detail })
        }
      }
    },

    gotoLogin() {
        this.$router.push('/tools/oldlogin?url=__tools__clublist')
    },

    async saveClub () {
      try {
        await this.$api.club.update_c_club({
          id: this.$route.query.id,
          token: this.oldlogin,
          address: this.clb.address,
          bankaccount_name: this.clb.bankaccount_name,
          bankaccount_iban: this.clb.bankaccount_iban,
          bankaccount_bic: this.clb.bankaccount_bic,
          email_admin: this.clb.email_admin,
          email_finance: this.clb.email_finance,
          email_interclub: this.clb.email_interclub,
          email_main: this.clb.email_main,
          name_long: this.clb.name_long,
          name_short: this.clb.name_short,
          venue: this.clb.venue,
          website: this.clb.website,
        })
        console.log('save successful')
        this.$root.$emit('snackbar', { text: 'Club saved' })
      } catch (error) {
        const reply = error.replyonse
        console.error('getting getClubs', reply)
        if (reply.status === 401) {
          this.gotoLogin()
        } else {
          this.$root.$emit('snackbar', { text: 'Saving club failed', reason: reply.data.detail })
        }
      }
    },

  }

}
</script>
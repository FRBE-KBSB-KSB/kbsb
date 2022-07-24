<template>
  <v-container>
    <p v-if="!club.idclub">{{ $t('Please select a club to view the enrollment') }}</p>
    <div v-if="club.idclub">
      <h3 v-show="status_consulting">{{ $t('Consulting club details') }}</h3>
      <h3 v-show="status_modifying">{{ $t('Modifying club details') }}</h3>
      <v-container>
        <v-row v-show="status_consulting">
          <v-col cols="12" sm="6" lg="4">
            <h4>{{ $t('Club details') }}</h4>
            <div>{{ $t('Long name') }}: {{ club.name_long }}</div>
            <div>{{ $t('Short name') }}: {{ club.name_short }}</div>
            <div>{{ $t('Federation') }}: {{ club.federation }}</div>
            <div>{{ $t('Club Venue') }}: {{ club.venue }}</div>
            <div>{{ $t('Website') }}: {{ club.website }}</div>
          </v-col>
          <v-col cols="12" sm="6" lg="4">
            <h4>{{ $t('Contact') }}</h4>
            <div>{{ $t('Main email address') }}: {{ club.email_main }}</div>
            <div>{{ $t('Email address Interclub') }}: {{ club.email_intercLub }}</div>
            <div>{{ $t('Email address administration') }}: {{ club.email_admin }}</div>
            <div>{{ $t('Email address finance') }}: {{ club.email_finance }}</div>
            <div>{{ $t('Postal address') }}: {{ club.address }}</div>
          </v-col>
          <v-col cols="12" sm="6" lg="4">
            <h4>{{ $t('Board Members') }}</h4>
            TO DO
          </v-col>
          <v-col cols="12" sm="6" lg="4">
            <h4>{{ $t('Bank details') }}</h4>
            <div>{{ $t('Bank account name') }}: {{ club.bankaccount_name }}</div>
            <div>{{ $t('Bank account IBAM') }}: {{ club.bankaccount_iban }}</div>
            <div>{{ $t('Bank account BIC') }}: {{ club.bankaccount_bic }}</div>
          </v-col>
          <v-col cols="12" sm="6" lg="4">
            <v-btn @click="modifyClub">{{ $t('Modify club') }}</v-btn>
          </v-col>
        </v-row>
        <v-row v-show="status_modifying">
          <v-col cols="12" sm="6" lg="4">
            <h4>{{ $t('Club details') }}</h4>
            <v-text-field v-model="club.name_long" :label="$t('Long name')" />
            <v-text-field v-model="club.name_short" :label="$t('Short name')" />
            <div>{{ $t('Federation') }}: {{ club.federation }}</div>
            <v-textarea v-model="club.venue" :label="$t('Venue')" />
            <v-text-field v-model="club.website" label="Website" />
          </v-col>
          <v-col cols="12" sm="6" lg="4">
            <h4>{{ $t('Contact') }}</h4>
            <v-text-field v-model="club.email_main" :label="$t('Main E-mail address')" />
            <v-text-field v-model="club.email_intercub" :label="$t('E-mail Interclub')" />
            <v-text-field v-model="club.email_admin" :label="$t('E-mail administration')" />
            <v-text-field v-model="club.email_finance" :label="$t('E-mail finance')" />
            <v-textarea v-model="club.address" :label="$t('Postal address')" />
          </v-col>
          <v-col cols="12" sm="6" lg="4">
            <h4>{{ $t('Board Members') }}</h4>
            TO DO
          </v-col>
          <v-col cols="12" sm="6" lg="4">
            <h4>{{ $t('Bank details') }}</h4>
            <v-text-field v-model="club.bankacount_name" :label="$t('Name bank account')" />
            <v-text-field v-model="club.bankaccount_iban" :label="$t('IBAN bank account')" />
            <v-text-field v-model="club.bankaccount_bic" :label="$t('BIC bank account')" />
          </v-col>
          <v-col cols="12" sm="6" lg="4">
            <v-btn @click="saveClub">{{ $t('Save club') }}</v-btn>
            <v-btn @click="cancelClub">{{ $t('Cancel') }}</v-btn>
          </v-col>
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

export default {

  name: 'Detail',

  data() {
    return {
      club: {},
      status: CLUB_STATUS.CONSULTING
    }
  },


  computed: {
    logintoken() { return this.$store.state.oldlogin.value },
    status_consulting() { return this.status == CLUB_STATUS.CONSULTING },
    status_modifying() { return this.status == CLUB_STATUS.MODIFYING },
  },

  methods: {

    cancelClub() {
      this.status = CLUB_STATUS.CONSULTING
      this.getClubDetails(this.club)
    },

    emitInterface() {
      this.$emit("interface", "getClubDetails", this.getClubDetails);
    },

    async getClubDetails(activeclub) {
      this.club = activeclub;
      try {
        const reply = await this.$api.club.get_c_club({
          id: this.club.id,
          token: this.logintoken
        })
        this.club = { ...reply.data }
      } catch (error) {
        const reply = error.reply
        if (reply.status === 401) {
          this.$router.push('/mgmt/login')
        }
        else {
          console.error('Getting club details failed', reply.data.detail)
          this.$root.$emit('snackbar', { text: this.$t('Getting club details failed') })
        }
      }
    },

    modifyClub() {
      // TODO check access rights
      this.status = CLUB_STATUS.MODIFYING
    },

    async saveClub() {
      try {
        console.log('Saving club', this.status)
        const reply2 = await this.$api.interclub.update_club({
          token: this.logintoken,
          idclub: this.club.idclub,
        })
        this.status = CLUB_STATUS.CONSULTING
      } catch (error) {
        const reply = error.response
        if (reply.status === 401) {
          this.gotoLogin()
        }
        else {
          console.error('Saving enrollment', reply.data.detail)
          this.$root.$emit('snackbar', { text: this.$t('Saving enrollment') })
        }
      }
    },

  },

  mounted() {
    this.emitInterface();
  },

}
</script>
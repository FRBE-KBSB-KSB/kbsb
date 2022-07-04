<template>
  <v-container>
    <p v-if="!club.idclub">{{ $t('Please select a club to view the enrollment') }}</p>
    <div v-if="club.idclub">
      <h3 v-show="status_consulting">{{ $t('Existing Enrollment') }}</h3>
      <h3 v-show="status_adding">{{ $t('Add Enrollment') }}</h3>
      <h3 v-show="status_modifying">{{ $t('Modify Enrollment') }}</h3>
      <div v-show="!enrollment.id && status_consulting">
        <p>{{ $t('The club is not enrolled yet') }}</p>
        <v-btn @click="newEnrollment">
          {{ $t('New enrollment') }}
        </v-btn>
      </div>
      <div v-show="enrollment.id && status_consulting">
        <ul>
          <li>{{ $t('Teams in division') }} 1: {{ enrollment.teams1 }}</li>
          <li>{{ $t('Teams in division') }} 2: {{ enrollment.teams2 }}</li>
          <li>{{ $t('Teams in division') }} 3: {{ enrollment.teams3 }} </li>
          <li>{{ $t('Teams in division') }} 4: {{ enrollment.teams4 }} </li>
          <li>{{ $t('Teams in division') }} 5: {{ enrollment.teams5 }}</li>
        </ul>
        <v-btn @click="modifyEnrollment">
          {{ $t('Modify enrollment') }}
        </v-btn>
      </div>
      <div v-show="status_adding || status_modifying">
        <v-text-field v-model="enrollment.teams1" :label="$t('Teams in division') + ' 1'" type="number" min="0"
          max="1" />
        <v-text-field v-model="enrollment.teams2" :label="$t('Teams in division') + ' 2'" type="number" min="0"
          max="15" />
        <v-text-field v-model="enrollment.teams3" :label="$t('Teams in division') + ' 3'" type="number" min="0"
          max="15" />
        <v-text-field v-model="enrollment.teams4" :label="$t('Teams in division') + ' 4'" type="number" min="0"
          max="15" />
        <v-text-field v-model="enrollment.teams5" :label="$t('Teams in division') + ' 5'" type="number" min="0"
          max="15" />
        <v-btn @click="saveEnrollment">
          {{ $t('Save enrollment') }}
        </v-btn>
        <v-btn @click="cancelEnrollment">
          {{ $t('Cancel') }}
        </v-btn>
      </div>
    </div>
  </v-container>
</template>
<script>
const ENROLLMENT_STATUS = {
  CONSULTING: 0,
  ADDING: 1,
  MODIFYING: 2,
}
const empty_enrollment = {
  teams1: 0,
  teams2: 0,
  teams3: 0,
  teams4: 0,
  teams5: 0,
}

export default {

  name: 'Enrollment',

  data() {
    return {
      club: {},
      enrollment: empty_enrollment,
      status: ENROLLMENT_STATUS.CONSULTING,
    }
  },


  computed: {
    logintoken() { return this.$store.state.oldlogin.value },
    status_adding() { return this.status == ENROLLMENT_STATUS.ADDING },
    status_consulting() { return this.status == ENROLLMENT_STATUS.CONSULTING },
    status_modifying() { return this.status == ENROLLMENT_STATUS.MODIFYING },
  },

  methods: {

    cancelEnrollment() {
      this.status = ENROLLMENT_STATUS.CONSULTING
      this.enrollment = empty_enrollment
    },

    emitInterface() {
      this.$emit("interface", "getAnonEnrollment", this.getAnonEnrollment);
    },

    async getAnonEnrollment(activeclub) {
      this.club = activeclub;
      try {
        const reply = await this.$api.interclub.anon_get_enrollment({
          idclub: this.club.idclub
        })
        if (reply.data) {
          this.enrollment = reply.data
        }
        else {
          this.enrollment.id = null
        }
      } catch (error) {
        const reply = error.response
        console.error('getting anon_enrollment', reply)
        if (reply.status === 401) {
          this.gotoLogin()
        }
        else {
          log.error('Getting existing enrollment failed', reply.data.detail)
          this.$root.$emit('snackbar', { text: this.$t('Getting existing enrollment failed') })
        }
      }
    },

    async newEnrollment() {
      try {
        const reply = await this.$api.club.verify_club_access({
          token: this.logintoken,
          idclub: this.club.idclub,
          role: "InterclubAdmin"
        })
        if (reply.data) {
          this.status = ENROLLMENT_STATUS.ADDING
        }
      } catch (error) {
        const reply = error.response
        if (reply.status === 401) {
          this.gotoLogin()
        }
        else {
          console.error('Getting accessrules club failed', reply.data.detail)
          this.$root.$emit('snackbar', { text: this.$t('Getting accessrules club failed') })
        }
      }
    },

    modifyEnrollment() {
      this.status = ENROLLMENT_STATUS.MODIFYING
    },

    async saveEnrollment() {
      try {
        console.log('Saving enrollment', this.status)
        if (this.status_adding) {
          const reply1 = await this.$api.interclub.make_enrollment({
            token: this.logintoken,
            idclub: this.club.idclub,
            teams1: this.enrollment.teams1,
            teams2: this.enrollment.teams2,
            teams3: this.enrollment.teams3,
            teams4: this.enrollment.teams4,
            teams5: this.enrollment.teams5,
          })
        }
        if (this.status_modifying) {
          const reply2 = await this.$api.interclub.update_enrollment({
            token: this.logintoken,
            idclub: this.club.idclub,
            teams1: this.enrollment.teams1,
            teams2: this.enrollment.teams2,
            teams3: this.enrollment.teams3,
            teams4: this.enrollment.teams4,
            teams5: this.enrollment.teams5,
          })
        }
        this.status = ENROLLMENT_STATUS.CONSULTING
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
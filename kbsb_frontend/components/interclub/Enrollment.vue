<template>
  <v-container>
    <p v-if="!club.idclub">{{ $t('Please select a club to view the enrollment') }}</p>
    <div v-if="club.idclub">
      <div v-show="status_consulting">
        <h3>{{ $t('Interclub enrollment') }}</h3>
        <div v-show="!enrollment.id">
          <p>{{ $t('The club is not enrolled yet') }}</p>
        </div>
        <div v-show="enrollment.id">
          <ul>
            <li>{{ $t('Teams in division') }} 1: {{ enrollment.teams1 }}</li>
            <li>{{ $t('Teams in division') }} 2: {{ enrollment.teams2 }}</li>
            <li>{{ $t('Teams in division') }} 3: {{ enrollment.teams3 }}</li>
            <li>{{ $t('Teams in division') }} 4: {{ enrollment.teams4 }}</li>
            <li>{{ $t('Teams in division') }} 5: {{ enrollment.teams5 }}</li>
          </ul>
        </div>
        <v-btn @click="modifyEnrollment">
          {{ $t('Modify enrollment') }}
        </v-btn>
      </div>
      <v-container v-show="status_modifying">
        <v-row>
          <v-col cols="12" sm="3">
            <h4>{{ $t('Teams') }}</h4>
            <v-text-field v-model="enrollment.teams1" :label="$t('Teams in division') + ' 1'"
              type="number" min="0" max="1" />
            <v-text-field v-model="enrollment.teams2" :label="$t('Teams in division') + ' 2'"
              type="number" min="0" max="15" />
            <v-text-field v-model="enrollment.teams3" :label="$t('Teams in division') + ' 3'"
              type="number" min="0" max="15" />
            <v-text-field v-model="enrollment.teams4" :label="$t('Teams in division') + ' 4'"
              type="number" min="0" max="15" />
            <v-text-field v-model="enrollment.teams5" :label="$t('Teams in division') + ' 5'"
              type="number" min="0" max="15" />
          </v-col>
          <v-col cols="12" sm="5">
            <h4>{{ $t('Wishes') }}</h4>
            <v-card class="elevation-4 mb-1">
              <v-card-text>
                <v-select :label="$t('Teams grouped by pairing number')"
                  v-model="enrollment.wishes.grouping" :items="grouping" />
              </v-card-text>
            </v-card>
            <v-card class="elevation-4 mb-1">
              <v-card-text>
                <v-select :label="$t('Distribution of teams in same division')"
                  v-model="enrollment.wishes.split" :items="splitting" />
              </v-card-text>
            </v-card>
            <v-card class="elevation-4">
              <v-card-text>
                <v-text-field v-model="enrollment.wishes.regional"
                  :label="$t('Regional preferences')" />
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="4">
            <h4>{{ $t('Remarks') }}</h4>
            <v-card class="elevation-4">
              <v-card-text>
                <v-textarea rows="5" v-model="enrollment.wishes.other" :label="$t('Remarks')" />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row>
          <v-btn @click="saveEnrollment">
            {{ $t('Save enrollment') }}
          </v-btn>
          <v-btn @click="cancelEnrollment">
            {{ $t('Cancel') }}
          </v-btn>
        </v-row>
      </v-container>
    </div>
  </v-container>
</template>
<script>
import Vue from 'vue'

const ENROLLMENT_STATUS = {
  CONSULTING: 0,
  MODIFYING: 1,
}
const empty_enrollment = {
  teams1: 0,
  teams2: 0,
  teams3: 0,
  teams4: 0,
  teams5: 0,
  wishes: {},
}

export default {

  name: 'Enrollment',

  data() {
    return {
      grouping: [
        { "text": this.$t("no preference"), "value": "0" },
        { "text": this.$t("1 group"), "value": "1" },
        { "text": this.$t("2 opposite groups"), "value": "2" },
      ],
      splitting: [
        { "text": this.$t("Don't split over multiple series"), "value": "1" },
        { "text": this.$t("Split over multiple series"), "value": "2" },
      ],
      enrollment: empty_enrollment,
      status: ENROLLMENT_STATUS.CONSULTING,
    }
  },

  props: {
    club: Object
  },

  computed: {
    logintoken() { return this.$store.state.oldlogin.value },
    status_consulting() { return this.status == ENROLLMENT_STATUS.CONSULTING },
    status_modifying() { return this.status == ENROLLMENT_STATUS.MODIFYING },
  },

  methods: {

    cancelEnrollment() {
      this.status = ENROLLMENT_STATUS.CONSULTING
      this.find_interclubenrollment()
    },

    emitInterface() {
      this.$emit("interface", "find_interclubenrollment", this.find_interclubenrollment);
    },

    async find_interclubenrollment() {
      if (!this.club.id) {
        this.enrollment = empty_enrollment
        return
      }
      try {
        const reply = await this.$api.interclub.find_interclubenrollment({
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
        if (reply.status === 401) {
          this.gotoLogin()
        }
        else {
          console.error('Getting existing enrollment failed', reply.data.detail)
          this.$root.$emit('snackbar', { text: this.$t('Getting existing enrollment failed') })
        }
      }
    },

    async modifyEnrollment() {
      try {
        const reply = await this.$api.club.verify_club_access({
          token: this.logintoken,
          idclub: this.club.idclub,
          role: "InterclubAdmin"
        })
        this.status = ENROLLMENT_STATUS.MODIFYING
      } catch (error) {
        const reply = error.response
        switch (reply.status) {
          case 401:
            this.gotoLogin()
            break;
          case 403:
            this.$root.$emit('snackbar', { text: this.$t("You don't have the access right to perfom this action") })
            break;
          default:
            console.error('Getting accessrules club failed', reply.data.detail)
            this.$root.$emit('snackbar', { text: this.$t('Getting accessrules club failed') })
        }
      }
    },

    async saveEnrollment() {
      try {
        const reply1 = await this.$api.interclub.set_interclubenrollment({
          token: this.logintoken,
          idclub: this.club.idclub,
          teams1: this.enrollment.teams1,
          teams2: this.enrollment.teams2,
          teams3: this.enrollment.teams3,
          teams4: this.enrollment.teams4,
          teams5: this.enrollment.teams5,
          wishes: this.enrollment.wishes,
        })
        this.status = ENROLLMENT_STATUS.CONSULTING
        this.find_interclubenrollment(this.club)
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
    this.$nextTick(() => {
      this.find_interclubenrollment();
    })
  },

}
</script>
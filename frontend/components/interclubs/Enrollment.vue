<script setup>
import { ref, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useIdtokenStore } from '@/store/idtoken'
import { useIdnumberStore } from '@/store/idnumber'
import { storeToRefs } from 'pinia'

// communication with manager
const emit = defineEmits(['displaySnackbar', 'changeDialogCounter'])
defineExpose({ setup })

// idtoken
const idstore = useIdtokenStore()
const { token: idtoken } = storeToRefs(idstore)
const idnstore = useIdnumberStore()
const { idnumber: idn } = storeToRefs(idnstore)
const { $backend } = useNuxtApp()

// i18n
const { t } = useI18n()

// datamodel// i18n
const empty_enrollment = {
  teams1: 0,
  teams2: 0,
  teams3: 0,
  teams4: 0,
  teams5: 0,
  wishes: {},
};
const enrollment = ref({ ...empty_enrollment})
const enr_status = ref('closed')
const modifying = ref(false)
const grouping = ref([
  { "text": t("No preference"), "value": "0" },
  { "text": t("1 group"), "value": "1" },
  { "text": t("2 opposite groups"), "value": "2" },
])
const splitting = ref([
  { "text": t("In 1 series"), "value": "1" },
  { "text": t("In multiple series"), "value": "2" },
])
const rules = ref({
  count20: (x) => (x && x.length <= 20 || 'Max 20 characters')
})
const club=ref({})


let icdata = {}

function cancelEnrollment() {
  this.status = INTERCLUBS_STATUS.CONSULTING
  this.find_interclubenrollment()
}

function calcstatus(){
  // we have the following status
  // - open
  // - closed
  // - noclub
  // - editing
  // - noaccess
  enr_status.value = 'closed'
  if (!icclub.id) {
    enr_status.value = 'noclub'
    return
  }
  if (modifying.value) {
    enr_status = 'editing'
    return
  }
  // TODO date check
  enr_status.value = 'open'

}

async function find_interclubenrollment() {
  let reply
  enrollment.value = { ...empty_enrollment }
  emit('changeDialogCounter', 1)
  try {
      reply = await $backend.find_interclubenrollment({
          idclub: club.value.idclub
      })
      if (reply.data) {
          enrollment.value = reply.data
          if (!enrollment.value.name.length) {
            enrollment.value.name = icclub.value.name_short
          }
      }
      else {
          enrollment.value.id = null
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
}

async function gotoLogin() {
  await router.push('/tools/oldlogin?url=__interclubs__manager')
}

async function modifyEnrollment() {
  try {
      const reply = await this.$api.club.verify_club_access({
          token: this.logintoken,
          idclub: this.club.idclub,
          role: "InterclubAdmin"
      })
      modifying.value = true
  } catch (error) {
      const reply = error.response
      switch (reply.status) {
          case 401:
              gotoLogin()
              break;
          case 403:
              this.$root.$emit('snackbar', { text: this.$t("You don't have the access right to perfom this action") })
              break;
          default:
              console.error('Getting accessrules club failed', reply.data.detail)
              this.$root.$emit('snackbar', { text: this.$t('Getting accessrules club failed') })
      }
  }
}

async function saveEnrollment() {
  // try {
  //   const reply1 = await this.$api.interclub.set_interclubenrollment({
  //       token: this.logintoken,
  //       idclub: this.club.idclub,
  //       name: this.enrollment.name,
  //       teams1: this.enrollment.teams1,
  //       teams2: this.enrollment.teams2,
  //       teams3: this.enrollment.teams3,
  //       teams4: this.enrollment.teams4,
  //       teams5: this.enrollment.teams5,
  //       wishes: this.enrollment.wishes,
  //   })
  //   this.status = INTERCLUBS_STATUS.CONSULTING
  //   this.find_interclubenrollment(this.club)
  // } catch (error) {
  //   const reply = error.response
  //   switch (reply.status) {
  //       case 401:
  //           this.gotoLogin()
  //           break;
  //       case 403:
  //           this.$root.$emit('snackbar', { text: this.$t("You don't have the access right to perfom this action") })
  //           break;
  //       default:
  //           console.error('Getting accessrules club failed', reply.data.detail)
  //           this.$root.$emit('snackbar', { text: this.$t('Saving enrollment failed') })
  //   }
  // }
}

async function setup(icclub, icdata_) {
  console.log('setup Enrollment', icclub, icdata_)
  icdata = icdata_
  await this.find_interclubenrollment()
}


</script>
<template>
  <v-container>
    <v-alert type="warning" variant="outlined" v-if="enr_status == 'closed'"
      :text="t('Currently the enrollment cannot be modified')" />
    <v-alert type="warning" variant="outlined" v-if="enr_status == 'noclub'"
      :text="t('Please select a club')" />
    <v-alert type="error" variant="outlined" v-if="enr_status == 'noaccess'"
      :text="t('Permission denied')" />   
    <div v-if="enr_status == 'open'">
      <v-row v-show="!enrollment.id">
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{ $t("Enrollment") }}
            </v-card-title>
            <v-card-text>
              {{ $t('The club is not enrolled yet') }}
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row v-show="enrollment.id">
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{ $t("Teams") }}
            </v-card-title>
            <v-card-text>
              <ul>
                <li>{{ $t('Teams in division') }} 1: {{ enrollment.teams1 }}
                </li>
                <li>{{ $t('Teams in division') }} 2: {{ enrollment.teams2 }}
                </li>
                <li>{{ $t('Teams in division') }} 3: {{ enrollment.teams3 }}
                </li>
                <li>{{ $t('Teams in division') }} 4: {{ enrollment.teams4 }}
                </li>
                <li>{{ $t('Teams in division') }} 5: {{ enrollment.teams5 }}
                </li>
              </ul>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{ $t("Wishes") }}
            </v-card-title>
            <v-card-text>
              <ul>
                <li>{{ $t('Teams grouped by pairing number') }}: {{
    groupingvalue }} </li>
                <li>{{ $t('Distribution of teams in same division') }}: {{
    splittingvalue }} </li>
                <li>{{ $t('Regional preferences') }}: {{
    enrollment.wishes.regional }} </li>
                <li>{{ $t('Remarks') }}: {{ enrollment.wishes.remarks }} </li>
              </ul>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{ $t("Name") }}
            </v-card-title>
            <v-card-text>
              {{ $t('Name of the club as shown in results and pairings') }}: {{
    enrollment.name }}
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-btn @click="modifyEnrollment" :disabled="new Date() > stopdate">
          {{ $t('Edit') }}
        </v-btn>
      </v-row>
    </div>
    <div v-if="enr_status == 'editing'">
      <v-row>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{ t('Teams') }}
            </v-card-title>
            <v-card-text>
              <p>{{ t('Number of teams per division') }}</p>
              <v-text-field v-model="enrollment.teams1" :label="t('Division') + ' 1'"
                type="number" min="0" max="1" />
              <v-text-field v-model="enrollment.teams2" :label="t('Division') + ' 2'"
                type="number" min="0" max="15" />
              <v-text-field v-model="enrollment.teams3" :label="t('Division') + ' 3'"
                type="number" min="0" max="15" />
              <v-text-field v-model="enrollment.teams4" :label="t('Division') + ' 4'"
                type="number" min="0" max="15" />
              <v-text-field v-model="enrollment.teams5" :label="t('Division') + ' 5'"
                type="number" min="0" max="15" />
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{ t('Wishes') }}
            </v-card-title>
            <v-card-text>
              <div>{{ t('Teams grouped by pairing number') }}</div>
              <v-select :label="t('Grouping')" v-model="enrollment.wishes.grouping"
                :items="grouping" />
              <div>{{ t('Distribution of teams in same division') }}</div>
              <v-select :label="t('Distribution')" v-model="enrollment.wishes.split"
                :items="splitting" />
              <div>{{ t('Regional preferences') }}</div>
              <v-text-field v-model="enrollment.wishes.regional" :label="t('Regional')" />
              <v-textarea rows="5" v-model="enrollment.wishes.remarks"
                :label="t('Other wishes')" />
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{ t('Name') }}
            </v-card-title>
            <v-card-text>
              {{ t('You can define a name for your club when the results and standings are displayed.') }}
              {{ t('As a default, your clubname is used.') }}
              <v-text-field v-model="enrollment.name" :label="$t('Name')" maxlength="20"
                :rules="[rules.count20]" />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-btn @click="saveEnrollment">
          {{ t('Save') }}
        </v-btn>&nbsp;
        <v-btn @click="cancelEnrollment">
          {{ t('Cancel') }}
        </v-btn>
      </v-row>
    </div>
  </v-container>
</template>

<script setup>
import { useMgmtTokenStore } from "@/store/mgmttoken";
import { storeToRefs } from 'pinia'
import { INTERCLUBS_STATUS, empty_enrollment } from '@/util/interclubs.js'

// communication with manager
const emit = defineEmits(['displaySnackbar',  'changeDialogCounter'])
const props = defineProps(["icclub", "round"])
defineExpose({ setup })

// idtoken
const mgmtstore = useMgmtTokenStore()
const {token: mgmttoken} = storeToRefs(mgmtstore)

const grouping = [
  { "text": "No preference", "value": "0" },
  { "text": "1 group", "value": "1" },
  { "text": "2 opposite groups", "value": "2" },
]
const splitting = [
  { "text": "In 1 series", "value": "1" },
  { "text": "In multiple series", "value": "2" },
]
const enrollment = ref({})
const club = ref(null)

async function get_interclubenrollment() {
  // console.log('find interclub enrollment', this.club.id, this.club.idclub)
  // if (!this.club.id) {
  //   this.enrollment = empty_enrollment
  //   return
  // }
  // this.enrollment = { ... empty_enrollment}
  // try {
  //   const reply = await this.$api.interclub.find_interclubenrollment({
  //     idclub: this.club.idclub
  //   })
  //   if (reply.data) {
  //     this.enrollment = reply.data
  //   }
  //   else {
  //     this.enrollment.id = null
  //   }
  // } catch (error) {
  //   const reply = error.response
  //   if (reply.status === 401) {
  //     this.gotoLogin()
  //   }
  //   else {
  //     console.error('Getting existing enrollment failed', reply.data.detail)
  //     this.$root.$emit('snackbar', { text: 'Getting existing enrollment failed' })
  //   }
  // }
}

function setup(){
  console.log('setup enrollment')
  enrollment.value = empty_enrollment
}
</script>

<style scoped?>
.fieldname {
  color: purple
}
</style>

<template>
  <v-container>
    <p v-if="!club.idclub">Please select a club to view the enrollment</p>
    <div v-if="club.idclub">
      <v-row v-show="!enrollment.id">
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              Enrollment
            </v-card-title>
            <v-card-text>
              The club is not enrolled yet
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
                <li><span class="fieldname">Teams in division 1:</span> {{ enrollment.teams1 }}</li>
                <li><span class="fieldname">Teams in division 2:</span> {{ enrollment.teams2 }}</li>
                <li><span class="fieldname">Teams in division 3:</span> {{ enrollment.teams3 }}</li>
                <li><span class="fieldname">Teams in division 4:</span> {{ enrollment.teams4 }}</li>
                <li>T<span class="fieldname">Teams in division 5:</span> {{ enrollment.teams5 }}</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

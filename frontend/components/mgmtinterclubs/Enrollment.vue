<script setup>
import { ref, computed } from 'vue'
import { useMgmtTokenStore } from "@/store/mgmttoken"
import { storeToRefs } from 'pinia'

// communication
defineExpose({ setup })
const mgmttokenstore = useMgmtTokenStore()
const { token: idtoken } = storeToRefs(mgmttokenstore)
const { $backend } = useNuxtApp()

//  snackbar and loading widgets
import ProgressLoading from '@/components/ProgressLoading.vue'
import SnackbarMessage from '@/components/SnackbarMessage.vue'
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

// datamodel
const empty_enrollment = {
  teams1: 0,
  teams2: 0,
  teams3: 0,
  teams4: 0,
  teams5: 0,
  wishes: {},
};
const enrollment = ref({ ...empty_enrollment })
const enr_status = ref('open')
const modifying = ref(false)
const grouping = ref([
  { "title": "No preference", "value": "0" },
  { "title": "1 group", "value": "1" },
  { "title": "2 opposite groups", "value": "2" },
])
const splitting = ref([
  { "title": "In 1 series", "value": "1" },
  { "title": "In multiple series", "value": "2" },
])

const rules = ref({
  count20: (x) => (x && x.length <= 20 || 'Max 20 characters')
})
let icclub = {}
let icdata = {}

// computed
const splittingvalue = computed(() => {
  let sp = splitting.value[0].title
  const val = enrollment.value.wishes.splitting || "2"
  splitting.value.forEach(e => {
    if (e.value == val) {
      sp = e.title
    }
  });
  return sp
})
const groupingvalue = computed(() => {
  let gr = grouping.value[0].title
  const val = enrollment.value.wishes.grouping || "0"
  grouping.value.forEach(e => {
    if (e.value == val) {
      gr = e.title
    }
  });
  return gr
})

async function cancelEnrollment() {
  enr_status.value = 'open'
  await find_interclubenrollment()
}

function calcstatus() {
  // we have the following status for the mgmt
  // - open
  // - noclub
  // - editing
  if (!icclub.id) {
    enr_status.value = 'noclub'
    return
  }
  if (modifying.value) {
    enr_status.value = 'editing'
    return
  }
  enr_status.value = 'open'

}

async function checkAccess() {
  return true
}

async function find_interclubenrollment() {
  if (!icclub.idclub) return
  let reply
  enrollment.value = { ...empty_enrollment }
  showLoading(true)
  try {
    reply = await $backend("interclub", "find_interclubenrollment", {
      idclub: icclub.idclub
    })
    readEnrollment(reply.data)
  }
  catch (error) {
    console.log('NOK find_interclubenrollment', error)
    if (error.code == 401) {
      gotoLogin()
    }
    else {
      showSnackbar('Getting existing enrollment failed')
    }
    return
  }
  finally {
    showLoading(false)
  }
}

async function gotoLogin() {
  await router.push('/tools/oldlogin?url=__interclubs__manager')
}

async function modifyEnrollment() {
  if (!modifying.value) {
    const allowed = await checkAccess()
    if (allowed) {
      modifying.value = true
    }
  }
  else {
    modifying.value = false
  }
  calcstatus()
}

function readEnrollment(data) {
  if (data) {
    enrollment.value = data
  }
  else {
    enrollment.value.id = null
  }
  if (!enrollment.value.name || !enrollment.value.name.length) {
    enrollment.value.name = icclub.name
  }
  if (!enrollment.value.wishes.grouping) {
    enrollment.value.wishes.grouping = "0"
  }
  if (!enrollment.value.wishes.splitting) {
    enrollment.value.wishes.splitting = "2"
  }
  console.log('enr', enrollment.value)
}


async function saveEnrollment() {
  let reply
  showLoading(true)

  try {
    reply = await $backend("interclub", "mgmt_set_interclubenrollment", {
      idclub: icclub.idclub,
      token: idtoken.value,
      name: enrollment.value.name,
      teams1: enrollment.value.teams1,
      teams2: enrollment.value.teams2,
      teams3: enrollment.value.teams3,
      teams4: enrollment.value.teams4,
      teams5: enrollment.value.teams5,
      wishes: enrollment.value.wishes,
    })
    modifying.value = false
    calcstatus()
    showSnackbar('Save OK')
  }
  catch (error) {
    console.log('NOK set_interclubenrollment', error)
    if (error.code == 401) {
      gotoLogin()
    }
    else {
      showSnackbar('Save failed')
    }
    return
  }
  finally {
    showLoading(false)
    await find_interclubenrollment()
  }
}

async function setup(icclub_, icdata_) {
  console.log('setup Enrollment', icclub_, icdata_)
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  icclub = icclub_
  icdata = icdata_
  calcstatus()
  await find_interclubenrollment()
}


</script>
<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />      
    <v-alert type="warning" variant="outlined" v-if="enr_status == 'noclub'"
      text="Select a club" />
    <div v-if="enr_status == 'open'">
      <v-row v-show="!enrollment.id">
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              Registation
            </v-card-title>
            <v-card-text>
              Not registered
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row v-show="enrollment.id">
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              Teams
            </v-card-title>
            <v-card-text>
              <ul>
                <li>Division 1: {{ enrollment.teams1 }}
                </li>
                <li>Division 2: {{ enrollment.teams2 }}
                </li>
                <li>Division 3: {{ enrollment.teams3 }}
                </li>
                <li>Division 4: {{ enrollment.teams4 }}
                </li>
                <li>Division 5: {{ enrollment.teams5 }}
                </li>
              </ul>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              Wishes
            </v-card-title>
            <v-card-text>
              <ul>
                <li>Teams group by pairing number: {{ groupingvalue }}</li>
                <li>Distribution of teams in single division: 
                  {{ splittingvalue }} </li>
                <li>Regional preferences: 
                  {{ enrollment.wishes.regional }} </li>
                <li>Remarks: {{ enrollment.wishes.remarks }} </li>
              </ul>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              Name of the club as displayed in results and standings
            </v-card-title>
            <v-card-text>
              Name: {{ enrollment.name }}
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-btn @click="modifyEnrollment">
          Edit
        </v-btn>
      </v-row>
    </div>
    <div v-if="enr_status == 'editing'">
      <v-row>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              Teams 
            </v-card-title>
            <v-card-text>
              <p>Number of temas per division</p>
              <v-text-field v-model="enrollment.teams1" label="Division 1'"
                type="number" min="0" max="1" />
              <v-text-field v-model="enrollment.teams2" label="Division 2'"
                type="number" min="0" max="15" />
              <v-text-field v-model="enrollment.teams3" label="Division 3'"
                type="number" min="0" max="15" />
              <v-text-field v-model="enrollment.teams4" label="Division 4'"
                type="number" min="0" max="15" />
              <v-text-field v-model="enrollment.teams5" label="Division 5'"
                type="number" min="0" max="15" />
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              Wishes
            </v-card-title>
            <v-card-text>
              <div>Teams group by pairing number</div>
              <v-select label="Grouping" v-model="enrollment.wishes.grouping"
                :items="grouping" />
              <div>Distribution of teams in same division</div>
              <v-select label="Distribution" v-model="enrollment.wishes.splitting"
                :items="splitting" />
              <div>Regional preferences</div>
              <v-text-field v-model="enrollment.wishes.regional" label="Regional" />
              <v-textarea rows="5" v-model="enrollment.wishes.remarks"
                label="Other wishes" />
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              Name of team as displayed in results and standings
            </v-card-title>
            <v-card-text>
              Name
              <v-text-field v-model="enrollment.name" label="Name" maxlength="20"
                :rules="[rules.count20]" />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-btn @click="saveEnrollment">
          Save
        </v-btn>&nbsp;
        <v-btn @click="cancelEnrollment">
          Cancel
        </v-btn>
      </v-row>
    </div>
  </v-container>
</template>

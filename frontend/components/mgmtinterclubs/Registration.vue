<script setup>
import { ref, computed } from "vue"
import { useMgmtTokenStore } from "@/store/mgmttoken"
import { storeToRefs } from "pinia"

// communication
defineExpose({ setup })
const mgmttokenstore = useMgmtTokenStore()
const { token: idtoken } = storeToRefs(mgmttokenstore)
const { $backend } = useNuxtApp()

//  snackbar and loading widgets
import ProgressLoading from "@/components/ProgressLoading.vue"
import SnackbarMessage from "@/components/SnackbarMessage.vue"
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

// datamodel
const empty_registration = {
  teams1: 0,
  teams2: 0,
  teams3: 0,
  teams4: 0,
  teams5: 0,
  wishes: {},
}
const registration = ref({ ...empty_registration })
const reg_status = ref("open")
const modifying = ref(false)
const grouping = ref([
  { title: "No preference", value: "0" },
  { title: "1 group", value: "1" },
  { title: "2 opposite groups", value: "2" },
])
const splitting = ref([
  { title: "In 1 series", value: "1" },
  { title: "In multiple series", value: "2" },
])

const rules = ref({
  count20: (x) => (x && x.length <= 20) || "Max 20 characters",
})
let icclub = {}
let icdata = {}

// computed
const splittingvalue = computed(() => {
  let sp = splitting.value[0].title
  const val = registration.value.wishes.splitting || "2"
  splitting.value.forEach((e) => {
    if (e.value == val) {
      sp = e.title
    }
  })
  return sp
})
const groupingvalue = computed(() => {
  let gr = grouping.value[0].title
  const val = registration.value.wishes.grouping || "0"
  grouping.value.forEach((e) => {
    if (e.value == val) {
      gr = e.title
    }
  })
  return gr
})

async function cancelRegistration() {
  reg_status.value = "open"
  await find_interclubregistration()
}

function calcstatus() {
  // we have the following status for the mgmt
  // - open
  // - noclub
  // - editing
  if (!icclub.idclub) {
    reg_status.value = "noclub"
    return
  }
  if (modifying.value) {
    reg_status.value = "editing"
    return
  }
  reg_status.value = "open"
}

async function checkAccess() {
  return true
}

async function find_interclubregistration() {
  if (!icclub.idclub) return
  let reply
  registration.value = { ...empty_registration }
  showLoading(true)
  try {
    reply = await $backend("interclub", "find_interclubregistration", {
      idclub: icclub.idclub,
    })
    readRegistration(reply.data)
  } catch (error) {
    console.log("NOK find_interclubregistration", error)
    if (error.code == 401) {
      gotoLogin()
    } else {
      showSnackbar("Getting existing registration failed")
    }
    return
  } finally {
    showLoading(false)
  }
}

async function gotoLogin() {
  await router.push("/tools/oldlogin?url=__interclubs__manager")
}

async function modifyRegistration() {
  if (!modifying.value) {
    const allowed = await checkAccess()
    if (allowed) {
      modifying.value = true
    }
  } else {
    modifying.value = false
  }
  calcstatus()
}

function readRegistration(data) {
  console.log("readRegistration", data)
  if (data) {
    registration.value = data
  } else {
    registration.value.id = null
  }
  if (!registration.value.name || !registration.value.name.length) {
    registration.value.name = icclub.name
  }
  if (!registration.value.wishes.grouping) {
    registration.value.wishes.grouping = "0"
  }
  if (!registration.value.wishes.splitting) {
    registration.value.wishes.splitting = "2"
  }
  console.log("reg", registration.value)
}

async function saveRegistration() {
  let reply
  showLoading(true)

  try {
    reply = await $backend("interclub", "mgmt_set_interclubregistration", {
      idclub: icclub.idclub,
      token: idtoken.value,
      name: registration.value.name,
      teams1: registration.value.teams1,
      teams2: registration.value.teams2,
      teams3: registration.value.teams3,
      teams4: registration.value.teams4,
      teams5: registration.value.teams5,
      wishes: registration.value.wishes,
    })
    modifying.value = false
    calcstatus()
    showSnackbar("Save OK")
  } catch (error) {
    console.log("NOK set_interclubregistration", error)
    if (error.code == 401) {
      gotoLogin()
    } else {
      showSnackbar("Save failed")
    }
    return
  } finally {
    showLoading(false)
    await find_interclubregistration()
  }
}

async function setup(icclub_, icdata_) {
  console.log("setup Registration", icclub_, icdata_)
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  icclub = icclub_
  icdata = icdata_
  calcstatus()
  await find_interclubregistration()
}
</script>
<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <v-alert
      type="warning"
      variant="outlined"
      v-if="reg_status == 'noclub'"
      text="Select a club"
    />
    <div v-if="reg_status == 'open'">
      <v-row v-show="!registration.id">
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title"> Registation </v-card-title>
            <v-card-text> Not registered </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row v-show="registration.id">
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title"> Teams </v-card-title>
            <v-card-text>
              <ul>
                <li>Division 1: {{ registration.teams1 }}</li>
                <li>Division 2: {{ registration.teams2 }}</li>
                <li>Division 3: {{ registration.teams3 }}</li>
                <li>Division 4: {{ registration.teams4 }}</li>
                <li>Division 5: {{ registration.teams5 }}</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title"> Wishes </v-card-title>
            <v-card-text>
              <ul>
                <li>Teams group by pairing number: {{ groupingvalue }}</li>
                <li>Distribution of teams in single division: {{ splittingvalue }}</li>
                <li>Regional preferences: {{ registration.wishes.regional }}</li>
                <li>Remarks: {{ registration.wishes.remarks }}</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title"> Display name team </v-card-title>
            <v-card-text> Name: {{ registration.name }} </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-btn @click="modifyRegistration"> Edit </v-btn>
      </v-row>
    </div>
    <div v-if="reg_status == 'editing'">
      <v-row>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title"> Teams </v-card-title>
            <v-card-text>
              <p>Number of temas per division</p>
              <v-text-field
                v-model="registration.teams1"
                label="Division 1'"
                type="number"
                min="0"
                max="1"
              />
              <v-text-field
                v-model="registration.teams2"
                label="Division 2'"
                type="number"
                min="0"
                max="15"
              />
              <v-text-field
                v-model="registration.teams3"
                label="Division 3'"
                type="number"
                min="0"
                max="15"
              />
              <v-text-field
                v-model="registration.teams4"
                label="Division 4'"
                type="number"
                min="0"
                max="15"
              />
              <v-text-field
                v-model="registration.teams5"
                label="Division 5'"
                type="number"
                min="0"
                max="15"
              />
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title"> Wishes </v-card-title>
            <v-card-text>
              <div>Teams group by pairing number</div>
              <v-select
                label="Grouping"
                v-model="registration.wishes.grouping"
                :items="grouping"
              />
              <div>Distribution of teams in same division</div>
              <v-select
                label="Distribution"
                v-model="registration.wishes.splitting"
                :items="splitting"
              />
              <div>Regional preferences</div>
              <v-text-field v-model="registration.wishes.regional" label="Regional" />
              <v-textarea
                rows="5"
                v-model="registration.wishes.remarks"
                label="Other wishes"
              />
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title"> Display name team </v-card-title>
            <v-card-text>
              Name
              <v-text-field
                v-model="registration.name"
                label="Name"
                maxlength="20"
                :rules="[rules.count20]"
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-btn @click="saveRegistration"> Save </v-btn>&nbsp;
        <v-btn @click="cancelRegistration"> Cancel </v-btn>
      </v-row>
    </div>
  </v-container>
</template>

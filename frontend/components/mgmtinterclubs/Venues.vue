<script setup>
import { ref, computed } from "vue"
import { useMgmtTokenStore } from "@/store/mgmttoken"
import { useMgmtInterclubStore } from "@/store/mgmtinterclub"
import { storeToRefs } from "pinia"

// communication with manager
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
const empty_venue = {
  address: "",
  email: "",
  phone: "",
  capacity: 0,
  remarks: "",
  rounds: "",
  teams: "",
  wheelchair: true,
}
let icclub = {}
let icdata = {}
const modifying = ref(false)
const ven_status = ref("open")
const venues = ref([])

// methods
function addVenue() {
  venues.value.push({ ...empty_venue })
}

async function cancel() {
  modifying.value = false
  await getICVenues()
  calcstatus()
}

function calcstatus() {
  console.log("calcstatus")
  // we have the following status
  // - open
  // - closed
  // - noclub
  // - noaccess
  if (!icclub.idclub) {
    ven_status.value = "noclub"
    return
  }
  if (modifying.value) {
    ven_status.value = "editing"
    return
  }
  ven_status.value = "open"
}

function deleteVenue(ix) {
  venues.value.splice(ix, 1)
}

async function getICVenues() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("interclub", "anon_getICVenues", {
      idclub: icclub.idclub,
    })
    readVenues(reply.data)
  } catch (error) {
    showSnackbar(error.message)
    return
  } finally {
    showLoading(false)
  }
}

function modifyICvenues() {
  modifying.value = true
  calcstatus()
}

function readVenues(data) {
  console.log("readvenues", data)
  venues.value = []
  if (data) {
    data.venues.forEach((v) => {
      let vn = { ...empty_venue, ...v }
      if (Array.isArray(vn.rounds) && vn.rounds.length) {
        vn.rounds_s = vn.rounds.join(",")
        vn.roundsel = "selected"
      } else {
        vn.rounds_s = ""
        vn.roundsel = "all"
      }
      if (Array.isArray(vn.teams) && vn.teams.length) {
        vn.teams_s = vn.teams.join(",")
        vn.teamssel = "selected"
      } else {
        vn.teams_s = ""
        vn.teamssel = "all"
      }
      venues.value.push(vn)
    })
  }
  console.log("venues read", venues.value)
}

async function saveVenues() {
  let reply
  venues.value.forEach((v) => {
    v.rounds = v.roundsel == "selected" ? v.rounds_s.split(",") : []
    v.teams = v.teamssel == "selected" ? v.teams_s.split(",") : []
  })
  console.log("venues", venues.value)
  showLoading(true)
  try {
    reply = await $backend("interclub", "mgmt_set_interclubvenues", {
      token: idtoken.value,
      idclub: icclub.idclub,
      venues: venues.value,
    })
    showSnackbar("Venues saved successfully")
  } catch (error) {
    console.log("NOK set_venue", error)
    if (error.code == 401) {
      ven_status.value = "noaccess"
    } else {
      showSnackbar("Saving venues failed: " + error.message)
    }
    return
  } finally {
    showLoading(false)
    await getICVenues()
  }
}

async function setup(icclub_, icdata_) {
  console.log("setup venues", icclub_, icdata_)
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  icclub = icclub_
  icdata = icdata_
  calcstatus()
  await getICVenues()
}
</script>

<template>
  <VContainer>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <h2>Interclub venues</h2>
    <p v-if="ven_status == 'noclub'">
      Please select a club to view the interclubs player list
    </p>
    <div v-if="ven_status == 'open'">
      <v-row v-show="!venues.length">
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title"> Venues </v-card-title>
            <v-card-text> No interclub venue is defined </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" sm="6" md="4" xl="3" v-for="(v, ix) in venues" :key="ix">
          <v-card class="elevation-5">
            <v-card-title> Venue: {{ ix + 1 }} </v-card-title>
            <v-card-text>
              <div>
                <b>Address:</b> <br />
                <span v-html="v.address.split('\n').join('<br />')"></span>
              </div>
              <div><b>Capacity in boards:</b> {{ v.capacity }}</div>
              <div><b>Teams:</b> {{ v.teams_s }}</div>
              <div><b>Rounds:</b> {{ v.rounds_s }}</div>
              <div><b>Accessible for wheelchair:</b> {{ v.wheelchair }}</div>
              <p>Optional</p>
              <div><b>Email address venue:</b> {{ v.email }}</div>
              <div><b>Telephone number venue:</b> {{ v.phone }}</div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-btn @click="modifyICvenues"> Edit </v-btn>
      </v-row>
    </div>
    <div v-if="ven_status == 'editing'">
      <v-row class="my-2">
        <v-btn @click="addVenue"> Add Venue </v-btn>
        <v-btn @click="saveVenues" class="ml-2"> Save Venues </v-btn>
        <v-btn @click="cancel" class="ml-2"> Cancel </v-btn>
      </v-row>
      <v-row>
        <v-col cols="12" sm="6" md="4" xl="3" v-for="(v, ix) in venues" :key="ix">
          <v-card class="elevation-5">
            <v-card-title> Venue: {{ ix + 1 }} </v-card-title>
            <v-card-text>
              <v-textarea v-model="v.address" label="Address" rows="3" outlined />
              <v-text-field
                v-model="v.capacity"
                label="Capacity (boards)"
                type="number"
              />
              <h4>Availability</h4>
              <v-radio-group v-model="v.roundsel">
                <v-radio value="all" label="All rounds" />
                <v-radio value="selected" label="Available for rounds" />
              </v-radio-group>
              <v-text-field
                v-show="v.roundsel == 'selected'"
                v-model="v.rounds_s"
                label="Rounds"
              />
              <v-radio-group v-model="v.teamssel">
                <v-radio value="all" label="All teams" />
                <v-radio value="selected" label="Available for teams" />
              </v-radio-group>
              <v-text-field
                v-show="v.teamssel == 'selected'"
                v-model="v.teams_s"
                label="Teams"
              />
              <v-checkbox v-model="v.wheelchair" label="Accessible for wheelchair" />
              <p class="fieldname">Optionally</p>
              <v-text-field v-model="v.email" label="Email address venue" />
              <v-text-field v-model="v.phone" label="Telephone number venue" />
              <v-textarea v-model="v.remarks" label="Remarks" />
            </v-card-text>
            <v-card-actions>
              <v-btn fab small @click="deleteVenue(ix)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </VContainer>
</template>

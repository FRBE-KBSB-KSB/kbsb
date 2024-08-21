<script setup>
import { ref, computed } from "vue"
import { useI18n } from "vue-i18n"
import { useIdtokenStore } from "@/store/idtoken"
import { storeToRefs } from "pinia"

// communication
defineExpose({ setup })
const idstore = useIdtokenStore()
const { token: idtoken } = storeToRefs(idstore)
const { $backend } = useNuxtApp()
const { t } = useI18n()

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
const venues = ref([])
const ven_status = ref("closed")
const modifying = ref(false)
let icclub = {}
let icdata = {}

function addVenue() {
  venues.value.push({ ...empty_venue })
}

async function cancel() {
  modifying.value = false
  await getICVenues()
  calcstatus()
}

function calcstatus() {
  // we have the following status
  // - open
  // - closed
  // - noclub
  // - editing
  // - noaccess
  ven_status.value = "closed"
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

async function checkAccess() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("club", "verify_club_access", {
      idclub: icclub.idclub,
      role: "InterclubAdmin,InterclubCaptain",
      token: idtoken.value,
    })
    return true
  } catch (error) {
    console.log("reply NOK", error)
    ven_status.value = "noaccess"
    showSnackbar(t("icn.perm_denied"))
    return false
  } finally {
    showLoading(false)
  }
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
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading(false)
  }
}

async function gotoLogin() {
  await router.push("/tools/oldlogin?url=__interclubs__manager")
}

async function modifyICvenues() {
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

function readVenues(data) {
  console.log("readvenues", data)
  venues.value = []
  if (data) {
    data.venues.forEach((v) => {
      let vn = { ...empty_venue, ...v }
      vn.rounds = vn.rounds.join(",")
      vn.roundsel = vn.rounds.length ? "selected" : "all"
      vn.teams = vn.teams.join(",")
      vn.teamssel = vn.rounds.length ? "selected" : "all"
      venues.value.push(vn)
    })
  }
  console.log("venues read", venues.value)
}

async function saveVenues() {
  let reply
  venues.value.forEach((v) => {
    v.rounds = v.roundsel == "selected" ? v.rounds.split(",") : []
    v.teams = v.teamssel == "selected" ? v.teams.split(",") : []
  })
  showLoading(true)
  try {
    reply = await $backend("interclub", "set_interclubvenues", {
      token: idtoken.value,
      idclub: icclub.idclub,
      venues: venues.value,
    })
    showSnackbar(t("icn.ven_save_ok"))
  } catch (error) {
    console.log("NOK set_venue", error)
    if (error.code == 401) {
      gotoLogin()
    } else {
      showSnackbar(t("icn.ven_save_fail"))
    }
    return
  } finally {
    showLoading(false)
    await getICVenues()
  }
}

async function setup(icclub_, icdata_) {
  console.log("setup Venue", icclub_, icdata_)
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  icclub = icclub_
  icdata = icdata_
  calcstatus()
  await getICVenues()
}
</script>
<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <v-alert
      type="warning"
      variant="outlined"
      v-if="ven_status == 'closed'"
      :text="t('icn.ven_closed')"
    />
    <v-alert
      type="warning"
      variant="outlined"
      v-if="ven_status == 'noclub'"
      :text="t('icn.select_club')"
    />
    <v-alert
      type="error"
      variant="outlined"
      v-if="ven_status == 'noaccess'"
      :text="t('icn.perm_denied')"
    />
    <div v-if="ven_status == 'open'">
      <v-row v-show="!venues.length">
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{ t("icn.ven_2") }}
            </v-card-title>
            <v-card-text>
              {{ t("icn.ven_notdefined") }}
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" sm="6" v-for="(v, ix) in venues" :key="ix">
          <v-card class="elevation-5">
            <v-card-title> {{ t("icn.ven_1") }}: {{ ix + 1 }} </v-card-title>
            <v-card-text>
              <div>
                <b>{{ t("Address") }}:</b> <br />
                <span v-html="v.address.split('\n').join('<br />')"></span>
              </div>
              <div>
                <b>{{ t("Capacity (boards)") }}:</b> {{ v.capacity }}
              </div>
              <div>
                <b>{{ t("Teams") }}:</b> {{ v.teams }}
              </div>
              <div>
                <b>{{ t("Rounds") }}:</b> {{ v.rounds }}
              </div>
              <div>
                <b>{{ t("icn.ven_wheelchair") }}:</b> {{ v.wheelchair }}
              </div>
              <p>{{ t("Optional") }}</p>
              <div>
                <b>{{ t("Email address") }} {{ t("icn.ven_1") }}:</b> {{ v.email }}
              </div>
              <div>
                <b>{{ t("Telephone number") }} {{ t("icn.ven_1") }}:</b> {{ v.phone }}
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-btn @click="modifyICvenues">
          {{ t("Edit") }}
        </v-btn>
      </v-row>
    </div>
    <div v-if="ven_status == 'editing'">
      <v-row class="my-2">
        <v-btn @click="addVenue()">
          {{ t("icn.ven_add") }}
        </v-btn>
        <v-btn @click="saveVenues" class="ml-2">
          {{ t("icn.ven_save") }}
        </v-btn>
        <v-btn @click="cancel" class="ml-2">
          {{ t("Cancel") }}
        </v-btn>
      </v-row>
      <v-row>
        <v-col cols="12" sm="6" v-for="(v, ix) in venues" :key="ix">
          <v-card class="elevation-5">
            <v-card-title> {{ t("icn.ven_1") }}: {{ ix + 1 }} </v-card-title>
            <v-card-text>
              <v-textarea
                v-model="v.address"
                :label="t('Address')"
                rows="3"
                @input="addEmptyVenue"
                outlined
              />
              <v-text-field
                v-model="v.capacity"
                :label="t('Capacity (boards)')"
                type="number"
              />
              <h4>{{ t("Availability") }}</h4>
              <v-radio-group v-model="v.roundsel">
                <v-radio value="all" :label="t('All rounds')" />
                <v-radio value="selected" :label="t('icn.ven_round_avail')" />
              </v-radio-group>
              <v-text-field
                v-show="v.roundsel == 'selected'"
                v-model="v.rounds"
                :label="t('icn.ven_round_sel')"
              />
              <v-radio-group v-model="v.teamssel">
                <v-radio value="all" :label="t('All teams')" />
                <v-radio value="selected" :label="t('icn.ven_teams_avail')" />
              </v-radio-group>
              <v-text-field
                v-show="v.teamssel == 'selected'"
                v-model="v.teams"
                :label="t('icn.ven_team_sel')"
              />
              <v-checkbox v-model="v.wheelchair" :label="t('icn.ven_wheelchair')" />
              <p class="fieldname">{{ t("Optionally") }}</p>
              <v-text-field
                v-model="v.email"
                :label="`${t('Email address')} ${t('icn.ven_1')}`"
              />
              <v-text-field
                v-model="v.phone"
                :label="`${t('Telephone number')} ${t('icn.ven_1')}`"
              />
              <v-textarea v-model="v.remarks" :label="t('Remarks')" />
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
  </v-container>
</template>

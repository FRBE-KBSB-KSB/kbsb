<script setup>
import { ref } from "vue"
import { useI18n } from "vue-i18n"

// communication
defineExpose({ setup })
const { t } = useI18n()
const { $backend } = useNuxtApp()

// snackbar and laoding weidgets
import ProgressLoading from "@/components/ProgressLoading.vue"
import SnackbarMessage from "@/components/SnackbarMessage.vue"
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

// data model
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
let icclub = {}
let icdata = {}

// methods alphabetically

function calcstatus() {
  // we have the following status
  // - open
  // - closed
  // - noclub
  if (!icclub.idclub) {
    ven_status.value = "noclub"
    return
  }
  ven_status.value = "open"
}

async function getICVenues() {
  let reply
  if (!icclub.idclub) {
    venues.value = []
    return
  }
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

function i18n_boole(v) {
  return v ? t("Yes") : t("No")
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

function selectClub() {
  getICVenues()
}

async function setup(idclub_, icdata_) {
  console.log("setup venue public", idclub_, icdata_)
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  icclub = { idclub: idclub_ }
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
      v-if="ven_status == 'noclub'"
      :text="t('icn.select_club')"
    />
    <div v-if="ven_status == 'open'">
      <h3>{{ $t("Interclub venues") }}</h3>
      <v-row>
        <v-col cols="12" sm="6" md="4" xl="3" v-for="(v, ix) in venues" :key="ix">
          <v-card class="elevation-5">
            <v-card-title> {{ $t("icn.ven_1") }}: {{ ix + 1 }} </v-card-title>
            <v-card-text>
              <div>
                <b>{{ $t("Address") }}:</b> <br />
                <span v-html="v.address.split('\n').join('<br />')"></span>
              </div>
              <div>
                <b>{{ $t("Capacity (boards)") }}:</b> {{ v.capacity }}
              </div>
              <div>
                <b>{{ t("icn.teams") }}:</b> {{ v.teams.join(", ") }}
              </div>
              <div>
                <b>{{ t("icn.rounds") }}:</b> {{ v.rounds.join(", ") }}
              </div>
              <div>
                <b>{{ t("icn.ven_wheelchair") }}:</b> {{ i18n_boole(v.wheelchair) }}
              </div>
              <div>
                <b>{{ t("icn.ven_parking") }}:</b> {{ v.parking }}
              </div>
              <div>
                <b>{{ t("Remarks") }}:</b> {{ v.remarks }}
              </div>
              <div>
                <b>{{ $t("Email address venue") }}:</b> {{ v.email }}
              </div>
              <div>
                <b>{{ $t("Telephone number venue") }}:</b> {{ v.phone }}
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

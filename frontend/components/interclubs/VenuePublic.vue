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
const idclub = ref(null)
const clubs = ref([])
const icvenues = ref([])

// methods alphabetically

function i18n_boole(v) {
  return v ? t("Yes") : t("No")
}

async function getClubs() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("club", "anon_get_clubs", {})
  } catch (error) {
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading(false)
  }
  clubs.value = reply.data
  clubs.value.forEach((p) => {
    p.merged = `${p.idclub}: ${p.name_short} ${p.name_long}`
  })
}

async function getICVenues() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("interclub", "anon_getICVenues", {
      idclub: idclub.value,
    })
  } catch (error) {
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading(false)
  }
  icvenues.value = reply.data.venues
}

function selectClub() {
  getICVenues()
}

async function setup() {
  console.log("setuo venue public")
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  getClubs()
}
</script>
<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <h2>{{ $t("Interclub venues") }}</h2>
    <v-card>
      <v-card-text>
        {{ $t("Select the club") }} ({{ $t("Start typing number or name") }})
        <VAutocomplete
          v-model="idclub"
          :items="clubs"
          item-title="merged"
          item-value="idclub"
          color="green"
          label="Club"
          clearable
          @update:model-value="getICVenues"
        >
        </VAutocomplete>
      </v-card-text>
    </v-card>
    <div v-if="idclub">
      <v-row v-show="!icvenues.length">
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{ $t("icn.ven_2") }}
            </v-card-title>
            <v-card-text>
              {{ $t("icn.ven_notdefined") }}
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" sm="6" md="4" xl="3" v-for="(v, ix) in icvenues" :key="ix">
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

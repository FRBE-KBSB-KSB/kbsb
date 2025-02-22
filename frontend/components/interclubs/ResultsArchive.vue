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

// datamodel
const idclub = ref(null)
const icclubs = ref([])
const icseries = ref([])
const round = ref("1")
let icdata = {}
const ic_rounds = ref([])

function addDetails(series, enc, games) {
  console.log("enc", enc.icclub_home, enc.pairingnr_home, games[0].fullname_home)
  const newlines = games.map((g) => {
    return {
      nature: "detail",
      idnumber_home: g.idnumber_home,
      fullname_home: g.fullname_home,
      rating_home: g.rating_home,
      idnumber_visit: g.idnumber_visit,
      fullname_visit: g.fullname_visit,
      rating_visit: g.rating_visit,
      result: g.result,
      overruled: g.overruled,
    }
  })
  const avg_home = Math.round(
    newlines.reduce((acc, current) => acc + current.rating_home, 0) / newlines.length
  )
  const avg_visit = Math.round(
    newlines.reduce((acc, current) => acc + current.rating_visit, 0) / newlines.length
  )
  const ix = series.lines.findIndex(
    (l) =>
      l.idclub_home == enc.icclub_home &&
      l.idclub_visit == enc.icclub_visit &&
      l.pairingnr_home == enc.pairingnr_home &&
      l.pairingnr_visit == enc.pairingnr_visit
  )
  console.log("ix", ix)
  if (enc.icclub_home && enc.icclub_visit && games.length) {
    series.lines.splice(ix + 1, 0, ...newlines, {
      nature: "average",
      avg_home,
      avg_visit,
    })
  }
}

async function getSeries() {
  let reply
  showLoading(true)
  console.log("getSeries", round.value, idclub.value)
  try {
    reply = await $backend("interclub", "anon_getICseries", {
      round: round.value,
      idclub: idclub.value,
    })
  } catch (error) {
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading(false)
  }
  icseries.value = reply.data
  icseries.value.forEach((s) => processSeries(s))
}

async function getClubs() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("interclub", "anon_getICclubs", {})
  } catch (error) {
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading(false)
  }
  icclubs.value = reply.data
  icclubs.value.forEach((p) => {
    p.merged = `${p.idclub}: ${p.name}`
  })
}

async function getICencounterdetails(series, enc) {
  let reply
  showLoading(true)
  try {
    reply = await $backend("interclub", "anon_getICencounterdetails", {
      division: series.division,
      index: series.index,
      round: round.value,
      icclub_home: enc.icclub_home,
      icclub_visit: enc.icclub_visit,
      pairingnr_home: enc.pairingnr_home,
      pairingnr_visit: enc.pairingnr_visit,
    })
  } catch (error) {
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading(false)
  }
  const details = reply.data
  addDetails(series, enc, details)
}

function isOverruled(game) {
  return game.overruled && game.overruled != "NOR"
}

function processSeries(s) {
  const names = Object.fromEntries(s.teams.map((t) => [t.pairingnumber, t.name]))
  s.showdetails = false
  s.lines = []
  s.rounds[0].encounters.forEach((enc) => {
    s.lines.push({
      nature: "teamresult",
      idclub_home: enc.icclub_home,
      idclub_visit: enc.icclub_visit,
      name_home: names[enc.pairingnr_home],
      name_visit: names[enc.pairingnr_visit],
      pairingnr_home: enc.pairingnr_home,
      pairingnr_visit: enc.pairingnr_visit,
      result: `${enc.boardpoint2_home / 2} - ${enc.boardpoint2_visit / 2}`,
    })
  })
}

function setup(icdata_) {
  console.log("setup results", icdata_)
  icdata = icdata_ || {}
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  ic_rounds.value = Object.keys(icdata.rounds || []).map((r) => {
    return { value: r, title: `R${r}: ${icdata.rounds[r]}` }
  })
  getClubs()
}

function updateDetails(s) {
  console.log("updateDetails", s.showdetails)
  if (s.showdetails) {
    s.rounds[0].encounters.forEach((enc) => getICencounterdetails(s, enc))
  } else {
    processSeries(s)
  }
}
</script>

<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <h2>{{ t("Results") }}</h2>
    <v-row>
      <v-col cols="12" sm="5">
        <VAutocomplete
          v-model="idclub"
          :items="icclubs"
          item-title="merged"
          item-value="idclub"
          color="green"
          label="Club"
          clearable
        >
        </VAutocomplete>
      </v-col>
      <v-col cols="8" sm="5">
        <VSelect v-model="round" :items="ic_rounds" :label="t('Round')"> </VSelect>
      </v-col>
      <v-col cols="4" sm="2">
        <VBtn icon="mdi-play" @click="getSeries"></VBtn>
      </v-col>
    </v-row>
    <v-card v-for="s in icseries" class="my-2">
      <v-card-title>
        <div class="d-flex justify-space-between">
          <h3>{{ t("Division") }} {{ s.division }}{{ s.index }}</h3>
          <div>
            <VCheckbox
              :label="t('Details')"
              v-model="s.showdetails"
              density="compact"
              hide-details
              @update:model-value="updateDetails(s)"
            />
          </div>
        </div>
      </v-card-title>
      <VDivider />
      <v-card-text>
        <div v-for="l in s.lines">
          <v-row v-show="l.nature == 'teamresult'" class="pt-2">
            <v-col cols="5"> {{ l.name_home }} ({{ l.idclub_home }} ) </v-col>
            <v-col cols="5"> {{ l.name_visit }} ({{ l.idclub_visit }}) </v-col>
            <v-col>
              {{ l.result }}
            </v-col>
          </v-row>
          <v-row v-show="l.nature == 'detail'" class="bg-green-lighten-5">
            <v-col cols="5" class="ml-5">
              {{ l.fullname_home }} ({{ l.rating_home }})
            </v-col>
            <v-col cols="5"> {{ l.fullname_visit }} ({{ l.rating_visit }}) </v-col>
            <v-col>
              <div v-show="isOverruled(l)" class="font-weight-bold text-purple-darken-2">
                {{ l.overruled }}
              </div>
              <div v-show="!isOverruled(l)">
                {{ l.result }}
              </div>
            </v-col>
          </v-row>
          <v-row v-show="l.nature == 'average'" class="bg-green-lighten-4">
            <v-col cols="5" class="ml-5">
              {{ t("Average ELO home") }} ({{ l.avg_home }})
            </v-col>
            <v-col cols="5"> {{ t("Average ELO visit") }} ({{ l.avg_visit }}) </v-col>
          </v-row>
        </div>
      </v-card-text>
    </v-card>
    <v-dialog width="10em" v-model="waitingdialog">
      <v-card>
        <v-card-title>{{ t("Loading...") }}</v-card-title>
        <v-card-text>
          <v-progress-circular indeterminate color="green" />
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.overruled {
  color: purple;
  font-weight: 500;
}
</style>

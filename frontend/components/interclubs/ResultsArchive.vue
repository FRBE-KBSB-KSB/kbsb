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
const season = ref("2324")
const ic_rounds = ref([])

function addDetails(series, enc, games) {
  console.log(
    "adddetails enc",
    enc.icclub_home,
    enc.pairingnr_home,
    games[0].fullname_home
  )
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
  const ix = series.lines.findIndex(
    (l) => l.idclub_home == enc.icclub_home && l.idclub_visit == enc.icclub_visit
    //  &&
    // l.pairingnr_home == enc.pairingnr_home &&
    // l.pairingnr_visit == enc.pairingnr_visit
  )
  console.log("ix", ix)
  if (enc.icclub_home && enc.icclub_visit && games.length) {
    series.lines.splice(ix + 1, 0, ...newlines)
  }
}

async function getSeries() {
  let reply
  showLoading(true)
  console.log("getICResultsArchive", round.value)
  try {
    reply = await $backend("interclub", "anon_getICResultsArchive", {
      round: round.value,
      season: season.value,
    })
  } catch (error) {
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading(false)
  }
  icseries.value = reply.data
  console.log("# icseries", icseries.value.length)
  icseries.value.forEach((s) => processSeries(s))
}

async function getICencounterdetails(series, enc) {
  let reply
  showLoading(true)
  try {
    reply = await $backend("interclub", "anon_getICencounterdetailsArchive", {
      season: season.value,
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
  console.log("process Series start", s.division, s.index)
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
      result: `${enc.boardpoint2_home / 2} - ${enc.boardpoint2_visit / 2}`,
    })
  })
  console.log("process Series done", s.division, s.index)
}

function setup(season_) {
  console.log("setup archive results", season_)
  season.value = season_
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  getSeries()
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
    <VSelect
      v-model="round"
      :items="[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]"
      :label="t('Round')"
      @update:modelValue="getSeries"
      max-width="10em"
    >
    </VSelect>
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
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<style scoped>
.overruled {
  color: purple;
  font-weight: 500;
}
</style>

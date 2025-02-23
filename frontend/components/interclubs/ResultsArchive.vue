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
const icseries = ref([])
const round = ref(1)
const season = ref("2324")

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

function processSeries(s) {
  const names = Object.fromEntries(s.teams.map((t) => [t.pairingnumber, t.name]))
  if (s.division == 1) {
    console.log("div 1", s)
    console.log("names", names)
  }
  s.lines = []
  s.rounds[0].encounters.forEach((enc) => {
    if (s.division == 1) {
      console.log("enc", enc)
    }
    s.lines.push({
      idclub_home: enc.icclub_home,
      idclub_visit: enc.icclub_visit,
      name_home: names[enc.pairingnr_home],
      name_visit: names[enc.pairingnr_visit],
      result: `${enc.boardpoint2_home / 2} - ${enc.boardpoint2_visit / 2}`,
    })
  })
  if (s.division == 1) {
    console.log("lines", s.lines)
  }
}

function setup(season_) {
  console.log("setup results", season_)
  season.value = season_
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  getSeries()
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
      <v-card-title> {{ t("Division") }} {{ s.division }}{{ s.index }} </v-card-title>
      <v-card-text>
        <div v-for="l in s.lines">
          <v-row class="pt-2">
            <v-col cols="5"> {{ l.name_home }} ({{ l.idclub_home }} ) </v-col>
            <v-col cols="5"> {{ l.name_visit }} ({{ l.idclub_visit }}) </v-col>
            <v-col>
              {{ l.result }}
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

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
const icstandings = ref([])
const icclub = ref([])
const idclub = ref(null)
const icdata = ref({})

function fillinDetails(s) {
  let stnrs = {}
  s.teams.forEach((t, ix) => {
    stnrs[t.pairingnumber] = ix
  })
  s.teams.forEach((t, ix) => {
    t.results = Array(12).join(" .").split(".")
    if (t.teamforfeit) {
      t.results.fill("TF")
    }
    t.results[ix] = "XX"
    t.games.forEach((g) => {
      let opponent = g.pairingnumber_opp
      t.results[stnrs[opponent]] = g.boardpoints2 / 2
    })
  })
}

async function getStandings() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("interclub", "anon_getICstandings", {
      idclub: idclub.value,
    })
  } catch (error) {
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading(false)
  }
  icstandings.value = reply.data
  sortStandings()
  icstandings.value.forEach((s) => {
    fillinDetails(s)
  })
}

async function setup(icclub_, icdata_) {
  icclub.value = icclub_
  icdata.value = icdata_
  idclub.value = icclub_.idclub
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  await getStandings()
}

function sortStandings() {
  icstandings.value.sort((a, b) => {
    if (a.division < b.division) return -1
    if (a.division > b.division) return 1
    if (a.index < b.index) return -1
    if (a.index > b.index) return 1
    return 0
  })
}
</script>

<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <h2>{{ $t("Standings") }}</h2>
    <v-card v-for="s in icstandings" class="my-2">
      <v-card-title>
        {{ $t("Division") }} {{ s.division }}{{ s.index }}
        <VDivider />
      </v-card-title>
      <v-card-text>
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Team</th>
              <th>1</th>
              <th>2</th>
              <th>3</th>
              <th>4</th>
              <th>5</th>
              <th>6</th>
              <th>7</th>
              <th>8</th>
              <th>9</th>
              <th>10</th>
              <th>11</th>
              <th>12</th>
              <th><b>MP</b></th>
              <th>BP</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(t, ix) in s.teams">
              <td>{{ ix + 1 }}</td>
              <td>{{ t.name }} ({{ t.idclub }})</td>
              <td>{{ t.results[0] }}</td>
              <td>{{ t.results[1] }}</td>
              <td>{{ t.results[2] }}</td>
              <td>{{ t.results[3] }}</td>
              <td>{{ t.results[4] }}</td>
              <td>{{ t.results[5] }}</td>
              <td>{{ t.results[6] }}</td>
              <td>{{ t.results[7] }}</td>
              <td>{{ t.results[8] }}</td>
              <td>{{ t.results[9] }}</td>
              <td>{{ t.results[10] }}</td>
              <td>{{ t.results[11] }}</td>
              <td>
                <b>{{ t.matchpoints }}</b>
              </td>
              <td>{{ t.boardpoints }}</td>
            </tr>
          </tbody>
        </table>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from "vue"
import { useMgmtTokenStore } from "@/store/mgmttoken"
import { storeToRefs } from "pinia"

// communication
defineExpose({ setup })
const mgmttokenstore = useMgmtTokenStore()
const { token: idtoken } = storeToRefs(mgmttokenstore)
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
const results = ref({})
let icdata = {}
let icclub = {}

async function getStandings() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("interclub", "anon_getICstandings", {
      idclub: icclub,
    })
  } catch (error) {
    showSnackbar(error.message)
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

function fillinDetails(s) {
  console.log("filling details:", s.division, s.index)
  let stnrs = {}
  s.teams.forEach((t, ix) => {
    stnrs[t.pairingnumber] = ix
  })
  console.log("stnrs", stnrs)
  s.teams.forEach((t, ix) => {
    t.results = Array(12).join(" .").split(".")
    if (t.teamforfeit) {
      t.results.fill("TF")
    }
    console.log("results", t.results)
    t.results[ix] = "XX"
    t.games.forEach((g) => {
      let opponent = g.pairingnumber_opp
      t.results[stnrs[opponent]] = g.boardpoints2 / 2
    })
  })
}

function setup(icclub_, icdata_) {
  console.log("setup standings", icclub_, icdata_)
  icdata = icdata_
  icclub = icclub_
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  getStandings()
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
    <h2>Standings</h2>
    <v-card v-for="s in icstandings" class="my-2">
      <v-card-title>
        Division {{ s.division }}{{ s.index }}
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

<script setup>
import { ref } from "vue"
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
const my = {
  idclub: 0,
  round: 0,
}
const playerlist_buffer = ref({})
let playersindexed = {}
const icseries = ref([])
const teamresults = ref([])
const showResults = ref(false)
let icdata = {}
let icclub = {}
const rsl_status = ref("noclub")

// methods alphabetically

function calc_points(enc) {
  let bphome = 0
  let bpvisit = 0
  let allfilled = true
  let teamforfeit = false
  enc.games.forEach((g) => {
    let result = g.overruled && g.overruled != "NOR" ? g.overruled : g.result
    switch (result) {
      case "1-0":
      case "1-0 FF":
        bphome += 2
        break
      case "½-½":
        bphome += 1
        bpvisit += 1
        break
      case "½-0":
        bphome += 1
        break
      case "0-½":
        bpvisit += 1
        break
      case "0-1":
      case "0-1 FF":
        bpvisit += 2
        break
      case "Team FF":
        teamforfeit = true
        break
      case "":
        allfilled = false
        break
    }
  })
  enc.boardpoints = `${bphome / 2}-${bpvisit / 2}`
  if (!allfilled) {
    enc.matchpoints = ""
  } else if (teamforfeit) {
    enc.matchpoints = "TFF"
  } else {
    if (bphome > bpvisit) enc.matchpoints = "2-0"
    if (bphome == bpvisit) enc.matchpoints = "1-1"
    if (bphome < bpvisit) enc.matchpoints = "0-2"
  }
}

function calcstatus() {
  // we have the following status
  // - open
  // - closed
  // - noclub
  // - noaccess
  if (!icclub.idclub) {
    rsl_status.value = "noclub"
    return
  }
  rsl_status.value = "open"
}

function clubLabel(pairingnr, teams) {
  let name = ""
  teams.forEach((t) => {
    if (t.pairingnumber == pairingnr) {
      name = t.name
      return
    }
  })
  return name
}

async function getICclub(clb_id) {
  if (playerlist_buffer.value[clb_id]) {
    console.log("playerlist in cache", clb_id)
    return
  }
  showLoading(true)
  try {
    let now = new Date()
    const reply = await $backend("interclub", "anon_getICclub", {
      idclub: clb_id,
    })
    console.log("calling anon_getICclub", clb_id, "in ms:", new Date() - now)
    showLoading(false)
    processICplayerlist(clb_id, reply.data)
  } catch (error) {
    console.error("calling anon_getICclub failed", clb_id, error)
    showSnackbar(error.message)
    return
  } finally {
    showLoading(false)
  }
}

async function getICSeries() {
  // get the pairing data limited to current round and club
  let reply
  if (!my.idclub || !my.round) {
    console.log("Skipping get ICseries: idclub or round not set")
    return
  }
  showLoading(true)
  try {
    reply = await $backend("interclub", "mgmt_getICseries", {
      round: my.round,
      idclub: my.idclub,
      token: idtoken.value,
    })
  } catch (error) {
    console.log("NOK", error)
    if (error.code == 401) {
      await navigateTo("/mgmt")
    }
    return
  } finally {
    icseries.value = reply.data
    showLoading(false)
    await processICSeries()
  }
}

function processICplayerlist(idclub, clubdata) {
  // processing the playerlist from the club details available in the store
  if (!idclub) return
  let players = []
  clubdata.players.forEach((p) => {
    if (!["assigned", "imported"].includes(p.nature)) return
    p.full = `${p.idnumber} ${p.last_name}, ${p.first_name}`
    players.push(p)
    playersindexed[p.idnumber] = p
  })
  playerlist_buffer.value[idclub] = players
}

async function processICSeries() {
  // process the pairing data received from the server
  let procencs = [] // encounters to be processed
  icseries.value.forEach((s) => {
    const { division, index } = s
    s.rounds[0].encounters.forEach((enc) => {
      // skip byes
      if (!enc.icclub_home || !enc.icclub_visit) return
      // skip encounters of other clubs
      if (![enc.icclub_home, enc.icclub_visit].includes(my.idclub)) return
      procencs.push({
        games: enc.games,
        division: division,
        index: index,
        icclub_home: enc.icclub_home,
        icclub_visit: enc.icclub_visit,
        name_home: clubLabel(enc.pairingnr_home, s.teams),
        name_visit: clubLabel(enc.pairingnr_visit, s.teams),
        nrgames: icdata.playerperdivision[division],
        pairingnr_home: enc.pairingnr_home,
        pairingnr_visit: enc.pairingnr_visit,
        round: s.rounds[0].round,
      })
    })
  })
  let tresults = [] // team results collector
  console.log("procencs", procencs)
  for (const enc of procencs) {
    await Promise.all([getICclub(enc.icclub_home), getICclub(enc.icclub_visit)])
    // fill in default games if not yet existing
    for (let i = enc.games.length; i < enc.nrgames; i++) {
      enc.games[i] = {
        idnumber_home: null,
        idnumber_visit: null,
        result: "", // NOTPLAYED
        overruled: "NOR", // NOTOVERRULED
      }
    }
    enc.games.forEach((g) => {
      if (g.idnumber_home == 0) g.idnumber_home = null
      if (g.idnumber_visit == 0) g.idnumber_visit = null
      if (!g.overruled) g.overruled = "NOR"
    })
    calc_points(enc)
    tresults.push(enc)
    teamresults.value = [...tresults.sort((a, b) => a.division - b.division)]
  }
}

async function saveResults() {
  let reply
  try {
    showLoading(true)
    reply = await $backend("interclub", "mgmt_saveICresults", {
      token: idtoken.value,
      results: teamresults.value,
    })
  } catch (error) {
    showSnackbar(error.message)
    return
  } finally {
    showLoading(false)
  }
  showSnackbar("Results saved")
}

async function setup(icclub_, round_, icdata_) {
  console.log("setup standings", icclub_, round_, icdata_)
  icdata = icdata_
  icclub = icclub_
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  calcstatus()
  teamresults.value = []
  icseries.value = []
  my.idclub = icclub_.idclub
  my.round = round_ ? parseInt(round_) : 0
  showResults.value = my.idclub && my.round
  await getICSeries()
  processICplayerlist()
}
</script>

<template>
  <VContainer>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <v-alert
      type="warning"
      variant="outlined"
      v-if="rsl_status == 'noclub'"
      text="Select club"
    />
    <div v-if="showResults && rsl_status == 'open'">
      <VBtn color="purple" @click="saveResults">Save results</VBtn>
      <v-card v-for="tr in teamresults" class="my-2">
        <v-card-title>
          Division {{ tr.division }}{{ tr.index }}: &nbsp; {{ tr.icclub_home }}
          {{ tr.name_home }} - {{ tr.icclub_visit }} {{ tr.name_visit }}
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-row v-for="(g, ix) in tr.games" class="d-flex">
              <v-col cols="4">
                <VAutocomplete
                  v-model="g.idnumber_home"
                  density="compact"
                  clearable
                  :items="playerlist_buffer[tr.icclub_home]"
                  item-title="full"
                  item-value="idnumber"
                  :label="`Player home ${ix + 1}`"
                  :hide-details="true"
                />
              </v-col>
              <v-col cols="2">
                <VSelect
                  v-model="g.result"
                  :items="resultchoices"
                  density="compact"
                  :hide-details="true"
                  @update:model-value="calc_points(tr)"
                />
              </v-col>
              <v-col col="4">
                <VAutocomplete
                  v-model="g.idnumber_visit"
                  density="compact"
                  :items="playerlist_buffer[tr.icclub_visit]"
                  item-title="full"
                  item-value="idnumber"
                  :label="`Player visit ${ix + 1}`"
                  :hide-details="true"
                  clearable
                />
              </v-col>
              <v-col cols="2">
                <VSelect
                  v-model="g.overruled"
                  :items="overrulechoices"
                  density="compact"
                  :hide-details="true"
                  @update:model-value="calc_points(tr)"
                />
              </v-col>
            </v-row>
            <VDivider />
            <v-row class="mt-1">
              <v-col cols="2"> MP: {{ tr.matchpoints }} </v-col>
              <v-col cols="2"> BP: {{ tr.boardpoints }} </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
      <VBtn color="purple" @click="saveResults">Save results</VBtn>
    </div>
  </VContainer>
</template>

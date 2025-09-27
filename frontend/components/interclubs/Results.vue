<script setup>
import { ref } from "vue"
import { useI18n } from "vue-i18n"
import { useIdtokenStore } from "@/store/idtoken"
import { useIdnumberStore } from "@/store/idnumber"
import { storeToRefs } from "pinia"

// communication
defineExpose({ setup })
const idstore = useIdtokenStore()
const { token: idtoken } = storeToRefs(idstore)
const idnstore = useIdnumberStore()
const { idnumber: idn } = storeToRefs(idnstore)
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
const idclub = ref(0)
const icclub = ref({})
const playerlist_buffer = ref({})
const players = ref([])
let playersindexed = {}
const icseries = ref([])
let round = 0
const teamresults = ref([])
const tr1 = ref({})
const rsl_status = ref("closed")
let icdata = {}
const overwriteDialog = ref(false)

// methods alphabetically

async function calcstatus() {
  // we have the following status
  // - open
  // - closed
  // - noclub
  // - noaccess
  // - notopenyet
  console.log("calcstatus", idclub.value)
  if (!idclub.value) {
    rsl_status.value = "noclub"
    players.value = []
    playersindexed = {}
    icseries.value = {}
    console.log("rsl_status", rsl_status.value)
    return
  }
  let access = await checkAccess()
  if (!access) {
    rsl_status.value = "noaccess"
    players.value = []
    playersindexed = {}
    icseries.value = {}
    console.log("rsl_status", rsl_status.value)
    return
  }
  const now = new Date().valueOf()
  const opened = new Date(icdata.rounds[round] + "T15:00").valueOf()
  const closed = opened + 3600000 * (9 + 24)
  console.log("dates", new Date(), new Date(icdata.rounds[round] + "T15:00"))
  if (now < opened) {
    rsl_status.value = "notopenyet"
    playerlist_buffer.value = {}
    teamresults.value = []
    icseries.value = []
    console.log("rsl_status", rsl_status.value)
    return
  }
  if (now > closed) {
    rsl_status.value = "closed"
    playerlist_buffer.value = {}
    teamresults.value = []
    icseries.value = []
    console.log("rsl_status", rsl_status.value)
    return
  }
  rsl_status.value = "open"
  console.log("rsl_status", rsl_status.value)
  if (!playerlist_buffer[idclub.value]) {
    getICplayerlist(icclub.value)
  }
  getICSeries()
}

function calc_points(enc) {
  let bphome = 0
  let bpvisit = 0
  let allfilled = true
  let teamforfeit = false
  enc.games.forEach((g) => {
    let result = isOverruled(g) ? g.overruled : g.result
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

async function checkAccess() {
  let reply
  if (!idtoken.value) return false
  showLoading(true)
  console.log("checkAccess idclub", idclub.value)
  try {
    reply = await $backend("club", "verify_club_access", {
      idclub: icclub.value.idclub,
      role: "InterclubAdmin,InterclubCaptain",
      token: idtoken.value,
    })
    return true
  } catch (error) {
    console.log("reply NOK", error)
    return false
  } finally {
    showLoading(false)
  }
}

function canSave(tr) {
  return !tr.played
}

function canOverwrite(tr) {
  return tr.played
}

function canSignHome(tr) {
  if (idclub.value == tr.icclub_home) {
    if (!tr.signhome_idnumber && tr.played) {
      return true
    }
  }
  return false
}

function canSignVisit(tr) {
  if (idclub.value == tr.icclub_visit) {
    if (!tr.signvisit_idnumber && tr.played) {
      return true
    }
  }
  return false
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

function getICplayerlist(ic_clb) {
  console.log("getICPlayerlist", ic_clb)
  if (!ic_clb && !ic_clb.idclub) return
  let players = ic_clb.players.filter((p) => ["assigned", "imported"].includes(p.nature))
  playerlist_buffer.value[ic_clb.idclub] = players
  players.forEach((p) => {
    p.full = `${p.idnumber} ${p.last_name}, ${p.first_name}`
    playersindexed[p.idnumber] = p
  })
}

async function getICclub(clb_id) {
  if (playerlist_buffer.value[clb_id]) {
    return
  }
  let reply
  showLoading(true)
  try {
    reply = await $backend("interclub", "anon_getICclub", {
      idclub: clb_id,
    })
  } catch (error) {
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading(false)
  }
  let cl = reply.data
  getICplayerlist(cl)
}

async function getICSeries() {
  console.log("getICseries")
  let reply
  showLoading(true)
  try {
    reply = await $backend("interclub", "clb_getICseries", {
      round: round,
      idclub: idclub.value,
      token: idtoken.value,
    })
  } catch (error) {
    console.log("NOK", error)
    if (error.code == 401) {
      rsl_status.value = "noaccess"
    }
    return
  } finally {
    showLoading(false)
  }
  icseries.value = reply.data
  console.log("aha")
  readICSeries()
}

function isOverruled(game) {
  return game.overruled && game.overruled != "NOR"
}

function openOverwrite(tr) {
  console.log("openOverwrite tr", tr, "tr1", tr1.value)
  tr1.value = tr
  console.log("openOverwrite tr1", tr1.value)
  overwriteDialog.value = true
}

function readICSeries() {
  console.log("readICSeries")
  let tra = []
  teamresults.value = []
  icseries.value.forEach((s) => {
    const { division, index } = s
    s.rounds[0].encounters.forEach(function (enc) {
      if (enc.icclub_home && enc.icclub_visit) {
        // skip byes
        if (enc.icclub_home == idclub.value || enc.icclub_visit == idclub.value) {
          getICclub(enc.icclub_home)
          getICclub(enc.icclub_visit)
          let tr = {
            division: division,
            games: enc.games,
            icclub_home: enc.icclub_home,
            icclub_visit: enc.icclub_visit,
            index: index,
            name_home: clubLabel(enc.pairingnr_home, s.teams),
            name_visit: clubLabel(enc.pairingnr_visit, s.teams),
            nrgames: icdata.playerperdivision[division],
            pairingnr_home: enc.pairingnr_home,
            pairingnr_visit: enc.pairingnr_visit,
            played: enc.played,
            round: round,
            signhome_idnumber: enc.signhome_idnumber,
            signhome_ts: enc.signhome_ts,
            signvisit_idnumber: enc.signvisit_idnumber,
            signvisit_ts: enc.signvisit_ts,
          }
          for (let i = tr.games.length; i < tr.nrgames; i++) {
            tr.games[i] = {
              idnumber_home: null,
              idnumber_visit: null,
              result: "",
            }
          }
          tr.games.forEach((g) => {
            if (g.idnumber_home == 0) g.idnumber_home = null
            if (g.idnumber_visit == 0) g.idnumber_visit = null
          })
          calc_points(tr)
          tra.push(tr)
        }
      }
    })
  })
  tra = tra.sort((a, b) => a.division - b.division)
  teamresults.value = [...tra]
}

async function saveResults(tr) {
  let reply
  try {
    showLoading(true)
    reply = await $backend("interclub", "clb_saveICresults", {
      token: idtoken.value,
      results: [tr],
    })
    overwriteDialog.value = false
    await getICSeries()
  } catch (error) {
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading(false)
  }
  showSnackbar(t("Results saved"))
}

async function setup(icclub_, round_, icdata_) {
  console.log("setup results", icdata_)
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  icclub.value = icclub_
  idclub.value = icclub.value.idclub
  round = round_
  icdata = icdata_
  idclub.value = icclub_.idclub
  await calcstatus()
}

async function sign(tr, who) {
  let plinpll = false
  console.log("tr", tr)
  if (who == "home") {
    const clb = tr.icclub_home
    console.log("clb", clb, "idn", idn.value)
    playerlist_buffer.value[clb].forEach((p) => {
      if (p.idnumber == idn.value) {
        console.log("idn belongs to club home")
        plinpll = true
      }
    })
    if (!plinpll && idn.value < 200000) {
      console.error("idn not in club home")
      return
    }
    tr.signhome_idnumber = idn
    tr.signhome_ts = new Date().toISOString()
  } else {
    const clb = tr.icclub_visit
    playerlist_buffer.value[clb].forEach((p) => {
      if (p.idnumber == idn.value) {
        console.log("idn belongs to club visit")
        plinpll = true
      }
    })
    if (!plinpll && idn.value < 200000) {
      console.error("idn not in club visit")
      return
    }
    tr.signvisit_idnumber = idn
    tr.signvisit_ts = new Date().toISOString()
  }
  await saveResults(tr)
}
</script>

<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <v-alert
      type="warning"
      v-if="rsl_status == 'noclub'"
      variant="outlined"
      closable
      :text="t('icn.select_club')"
    />
    <v-alert
      type="error"
      v-if="rsl_status == 'noaccess'"
      variant="outlined"
      closable
      :text="t('icn.perm_denied')"
    />
    <v-alert
      type="warning"
      v-if="rsl_status == 'notopenyet'"
      variant="outlined"
      closable
      :text="t('Entry of the results starts on Sunday at 15h')"
    />
    <v-alert
      type="warning"
      variant="outlined"
      v-if="rsl_status == 'closed'"
      closable
      :text="t('icn.results_closed')"
    />
    <div v-if="rsl_status == 'open'">
      <v-card v-for="tr in teamresults" class="my-2">
        <v-card-title>
          {{ t("Division") }} {{ tr.division }}{{ tr.index }}: &nbsp;
          {{ tr.icclub_home }} {{ tr.name_home }} - {{ tr.icclub_visit }}
          {{ tr.name_visit }}
        </v-card-title>
        <v-card-text>
          Uitslagen
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
                  :label="t('Player home') + ' ' + (ix + 1)"
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
              <v-col cols="4">
                <VAutocomplete
                  v-model="g.idnumber_visit"
                  density="compact"
                  :items="playerlist_buffer[tr.icclub_visit]"
                  item-title="full"
                  item-value="idnumber"
                  :label="t('Player visit') + ' ' + (ix + 1)"
                  :hide-details="true"
                  clearable
                />
              </v-col>
              <v-col cols="2">
                <div v-show="isOverruled(g)" class="text-purple font-weight-bold">
                  {{ g.overruled }}
                </div>
              </v-col>
            </v-row>
            <VDivider />
            <v-row class="mt-1">
              <v-col cols="" v-show="canSave(tr)">
                <VBtn color="green" @click="saveResults(tr)">{{
                  t("Save results")
                }}</VBtn>
              </v-col>
              <v-col cols="4" v-show="canOverwrite(tr)">
                <VBtn color="green" @click="openOverwrite(tr)">{{
                  t("Overwrite results")
                }}</VBtn>
              </v-col>
            </v-row>
            <v-row class="mt-1">
              <v-col cols="4">
                {{ t("signature") }} {{ t("home") }}: {{ tr.signhome_idnumber }}
                <v-btn
                  @click="sign(tr, 'home')"
                  color="green"
                  density="compact"
                  v-show="canSignHome(tr)"
                >
                  {{ t("sign") }}
                </v-btn>
              </v-col>
              <v-col cols="2"> MP: {{ tr.matchpoints }} </v-col>
              <v-col cols="2"> BP: {{ tr.boardpoints }} </v-col>
              <v-col col="4">
                {{ t("signature") }} {{ t("away") }}: {{ tr.signvisit_idnumber }}
                <v-btn
                  @click="sign(tr, 'away')"
                  color="green"
                  density="compact"
                  v-show="canSignVisit(tr)"
                >
                  {{ t("sign") }}
                </v-btn>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
    </div>
    <VDialog v-model="overwriteDialog" width="30em">
      <VCard>
        <VCardTitle>
          {{ t("icn.res_overwritetitle") }} {{ tr1.name_home }} - {{ tr1.name_visit }}
          <VDivider />
        </VCardTitle>
        <VCardText>
          <p>{{ t("icn.res_overwriteinfo") }}</p>
          <p>{{ t("icn.res_overwriteconfirm") }}</p>
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn @click="saveResults(tr1)">{{ t("icn.res_overwrite") }}</VBtn>
          <VBtn @click="overwriteDialog = false">{{ t("Cancel") }}</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>
  </v-container>
</template>

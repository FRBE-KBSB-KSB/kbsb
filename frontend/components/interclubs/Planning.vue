<script setup>
import { ref } from "vue"
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
let playersindexed = {}
const players = ref([])
const icseries = ref({})
const icclub = ref({})
const idclub = ref(0)
let round = 0
const teamsplanning = ref({})
const pln_status = ref("closed")
let icdata = {}

async function calcstatus() {
  // we have the following status
  // - open
  // - closed
  // - noclub
  // - noaccess
  // - expired
  console.log("calcstatus", idclub.value)
  if (!idclub.value) {
    pln_status.value = "noclub"
    players.value = []
    playersindexed = {}
    icseries.value = {}
    return
  }
  let access = await checkAccess()
  if (!access) {
    pln_status.value = "noaccess"
    players.value = []
    playersindexed = {}
    icseries.value = {}
    return
  }
  readICclub()
  const now = new Date()
  const expiry = new Date(icdata.rounds[round] + "T14:00")
  console.log("dates", now, expiry)
  if (now.valueOf() > expiry.valueOf) {
    pln_status.value = "expired"
    players.value = []
    playersindexed = {}
    icseries.value = {}
    return
  }
  pln_status.value = "open"
  await getICseries()
}

async function checkAccess() {
  let reply
  showLoading(true)
  console.log("checkAccess idclub", icclub.idclub)
  try {
    reply = await $backend("club", "verify_club_access", {
      idclub: icclub.value.idclub,
      role: "InterclubAdmin,InterclubCaptain",
      token: idtoken.value,
    })
    return true
  } catch (error) {
    console.log("reply NOK", error)
    showSnackbar(t("icn.perm_denied"))
    return false
  } finally {
    showLoading(false)
  }
}

function clubLabel(pairingnr, s) {
  let name = ""
  s.teams.forEach((t) => {
    if (t.pairingnumber == pairingnr) {
      name = t.name
      return
    }
  })
  return name
}

async function getICseries() {
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
      gotoLogin()
    }
    return
  } finally {
    showLoading(false)
  }
  icseries.value = reply.data
  teamsplanning.value = []
  readICplanning()
}

async function gotoLogin() {
  await router.push("/tools/oldlogin?url=__interclubs__manager")
}

async function readICclub() {
  console.log("readICclub")
  players.value = []
  playersindexed.value = {}
  teamsplanning.value = {}
  console.log("icclub", icclub.value)
  icclub.value.players.forEach((p) => {
    if (p.nature != "exported") {
      let player = {}
      let tit = p.titular ? `:: ${t("Titular")} ${p.titular}` : ""
      if (p.nature != "exported") {
        player.first_name = p.first_name
        player.last_name = p.last_name
        player.assignedrating = p.assignedrating
        player.idnumber = p.idnumber
        player.titular = p.titular
        player.full = `${p.idnumber}: ${p.last_name}, ${p.first_name} -- ${p.assignedrating} ${tit}`
      }
      players.value.push(player)
      playersindexed[p.idnumber] = player
    }
  })
  console.log("players", players.value)
}

function readICplanning() {
  console.log("readICplanning")
  icseries.value.forEach((s) => {
    // fill in Teams
    s.teams.forEach((t) => {
      let sround = s.rounds[0]
      if (t.idclub == idclub.value) {
        let team = {
          division: t.division,
          games: [],
          idclub: idclub.value,
          index: s.index,
          pairingnumber: t.pairingnumber,
          name: t.name,
          nrgames: icdata.playerperdivision[t.division],
          round: parseInt(round),
        }
        let avg = 0
        let allassigned = true
        sround.encounters.forEach((enc, encix) => {
          if (enc.icclub_home == idclub.value && enc.pairingnr_home == t.pairingnumber) {
            team.playinghome = true
            team.idclub_opponent = enc.icclub_visit
            team.name_opponent = clubLabel(enc.pairingnr_visit, s)
            team.games = enc.games
          } else if (
            enc.icclub_visit == idclub.value &&
            enc.pairingnr_visit == t.pairingnumber
          ) {
            team.playinghome = false
            team.idclub_opponent = enc.icclub_home
            team.name_opponent = clubLabel(enc.pairingnr_home, s)
            team.games = enc.games
          }
        })
        for (let i = team.games.length; i < team.nrgames; i++) {
          team.games[i] = {
            idnumber_home: null,
            idnumber_visit: null,
            result: "",
          }
        }
        team.games.forEach((g) => {
          if (g.idnumber_home == 0) g.idnumber_home = null
          if (g.idnumber_visit == 0) g.idnumber_visit = null
          if (team.playinghome) {
            if (!g.idnumber_home) {
              allassigned = false
            } else {
              avg += playersindexed[g.idnumber_home].assignedrating
            }
          } else {
            if (!g.idnumber_visit) {
              allassigned = false
            } else {
              avg += playersindexed[g.idnumber_visit].assignedrating
            }
          }
          team.average = allassigned ? avg / team.nrgames : 0
        })
        // do nothing it for BYE
        if (team.idclub_opponent) teamsplanning.value.push(team)
      }
    })
  })
}

async function savePlanning() {
  let reply
  showLoading(true)
  console.log("saving planning", teamsplanning.value)
  try {
    reply = await $backend("interclub", "clb_saveICplanning", {
      token: idtoken.value,
      plannings: teamsplanning.value,
    })
  } catch (error) {
    if (error.code == 401) gotoLogin()
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading(false)
  }
  showSnackbar(t("Planning saved"))
  getICseries()
}

async function setup(icclub_, round_, icdata_) {
  console.log("setup planning", icclub_, round_, icdata_)
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  icclub.value = icclub_
  idclub.value = icclub_.idclub
  icdata = icdata_
  round = round_
  await calcstatus()
}

function validatePlanning() {
  let reply
  savePlanning()
}
</script>
<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <v-alert
      type="warning"
      variant="outlined"
      v-if="pln_status == 'closed'"
      :text="t('icn.planning_closed')"
    />
    <v-alert
      type="warning"
      variant="outlined"
      v-if="pln_status == 'noclub'"
      :text="t('icn.select_club')"
    />
    <v-alert
      type="error"
      variant="outlined"
      v-if="pln_status == 'noaccess'"
      :text="t('icn.perm_denied')"
    />
    <v-alert
      type="warning"
      variant="outlined"
      v-if="pln_status == 'expired'"
      :text="t('You can no longer modify the planning of this round')"
    />
    <div v-if="pln_status == 'open'">
      <VCard v-for="(tp, ix) in teamsplanning" class="my-2">
        <VCardTitle>
          {{ tp.name }}
        </VCardTitle>
        <VCardSubtitle class="d-flex">
          <div v-show="tp.playinghome" class="flex-1-1-100">
            {{ tp.idclub }} {{ tp.name }} - {{ tp.idclub_opponent }}
            {{ tp.name_opponent }}
          </div>
          <div v-show="!tp.playinghome" class="flex-1-1-100">
            {{ tp.idclub_opponent }} {{ tp.name_opponent }} - {{ tp.idclub }}
            {{ tp.name }}
          </div>
          <div class="flex-0-0">{{ t("Average ELO") }}: {{ tp.average }}</div>
          <VDivider />
        </VCardSubtitle>
        <VCardText>
          <div v-for="(g, ix) in tp.games">
            <VAutocomplete
              v-model="g.idnumber_home"
              density="compact"
              :items="players"
              item-title="full"
              item-value="idnumber"
              :label="t('Player') + ' ' + (ix + 1)"
              :hide-details="true"
              v-show="tp.playinghome"
              clearable
            />
            <VAutocomplete
              v-model="g.idnumber_visit"
              density="compact"
              :items="players"
              item-title="full"
              item-value="idnumber"
              :label="t('Player') + ' ' + (ix + 1)"
              :hide-details="true"
              v-show="!tp.playinghome"
              clearable
            />
          </div>
        </VCardText>
      </VCard>
      <div v-show="icseries.length">
        <VBtn @click="validatePlanning()" color="primary">{{ t("Save") }}</VBtn>
      </div>
    </div>
  </v-container>
</template>

<style scoped>
.imported {
  color: purple;
  font-weight: 500;
}

.exported {
  color: rgb(186, 185, 185);
}
</style>

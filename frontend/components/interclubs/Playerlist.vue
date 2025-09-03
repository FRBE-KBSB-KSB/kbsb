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

// dialog
const assigndialog = ref(false)
const editelodialog = ref(false)
const edittitulardialog = ref(false)
const transferalldialog = ref(false)
const transferdialog = ref(false)
const unassigndialog = ref(false)

// datamodel
const clubmembers = ref([])
const icclub = ref({})
const idclub = ref(0)
const registered = ref(null)
let playersindexed = {}
const players = ref([])
const playeredit = ref({})
const exportallvisit = ref(0)
const titnotit = ref("notit")
const titularchoices = []
const pll_status = ref("closed")
let pll_period
let pll_startdate
let pll_enddate
let pll = false
let mininmal_assignelo = 3000
let icdata = { playerlist_data: [] }
let clubmembers_cache_idclub = null

// validation
const validationdialog = ref(false)
const validationerrors = ref([])

// data table definiton
const headers = [
  { title: "N", key: "index" },
  { title: t("Name"), key: "fullname" },
  { title: t("ID number"), key: "idnumber", sortable: false },
  { title: "ELO", key: "assignedrating" },
  { title: "F-ELO", key: "fiderating" },
  { title: "B-ELO", key: "natrating" },
  { title: "Club", key: "idcluborig" },
  { title: t("Titular"), key: "titular" },
  { title: t("icn.pll_mindiv"), key: "mindiv" },
  { title: t("Actions"), key: "action" },
]
const itemsPerPage = 50
const itemsPerPageOptions = [
  { value: 50, title: "50" },
  { value: 150, title: "150" },
  { value: -1, title: "All" },
]

// methods alphabetically

function calc_period() {
  const now = new Date()
  pll_period = "unknown"
  icdata.playerlist_data.forEach((p) => {
    let start = new Date(p.start)
    let end = new Date(p.end)
    if (now.valueOf() > start.valueOf() && now.valueOf() < end.valueOf()) {
      pll_period = p.period
      pll_startdate = p.start
      pll_enddate = p.end
      pll = true
      return
    }
  })
  console.log("pll_period", pll_period)
}

async function calc_status() {
  // we have the following status
  // - open
  // - closed
  // - noclub
  // - noaccess
  if (!idclub.value) {
    pll_status.value = "noclub"
    console.log("calc_status noclub")
    return
  }
  let access = await checkAccess()
  if (!access) {
    pll_status.value = "noaccess"
    console.log("calc_status noaccess")
    return
  }
  pll_status.value = pll ? "open" : "closed"
  console.log("calc_status closed")
}

function canAssign(idnumber) {
  return [PLAYERSTATUS.unassigned, PLAYERSTATUS.exported].includes(
    playersindexed[idnumber].nature
  )
}

function canEditElo(idnumber) {
  if (pll_period == "september") {
    return [PLAYERSTATUS.assigned, PLAYERSTATUS.imported].includes(
      playersindexed[idnumber].nature
    )
  }
  if (pll_period == "november") {
    return (
      playersindexed[idnumber].nature == PLAYERSTATUS.unassigned ||
      playersindexed[idnumber].period == "november"
    )
  }
  if (pll_period == "january") {
    return (
      playersindexed[idnumber].nature == PLAYERSTATUS.unassigned ||
      playersindexed[idnumber].period == "january"
    )
  }
}

function canExport(idnumber) {
  if (pll_period == "september") {
    return [PLAYERSTATUS.assigned, PLAYERSTATUS.unassigned].includes(
      playersindexed[idnumber].nature
    )
  } else {
    return false
  }
}

function canEditTitular(idnumber) {
  if (pll_period == "september") {
    return [PLAYERSTATUS.assigned, PLAYERSTATUS.imported].includes(
      playersindexed[idnumber].nature
    )
  } else {
    return false
  }
}

function canUnassign(idnumber) {
  return [PLAYERSTATUS.assigned, PLAYERSTATUS.imported].includes(
    playersindexed[idnumber].nature
  )
}

async function checkAccess() {
  let reply
  if (!idtoken.value) return false
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
    pll_status.value = "noaccess"
    return false
  } finally {
    showLoading(false)
  }
}

function fillinPlayerList() {
  console.log("fillinPlayerList")
  // add new members to the playerlist
  let pnature = PLAYERSTATUS.unassigned
  mininmal_assignelo = 3000
  if (registered.value && !players.value.length) {
    // automatically make players assigned at the start of the Interclubs
    pnature = PLAYERSTATUS.assigned
  }
  console.log("clubmembers", clubmembers.value.length ? clubmembers.value[0] : "empty")
  // first fix period of already assigned players
  players.value.forEach((p) => {
    if (p.period == "unknown") {
      p.period = "september"
    }
  })
  clubmembers.value.forEach((m) => {
    if (!playersindexed[m.idnumber]) {
      let fiderating = m.fiderating ? m.fiderating : 0
      let natrating = m.natrating ? m.natrating : 0
      let calcrating = fiderating > 0 ? fiderating : natrating
      let newplayer = {
        assignedrating: calcrating,
        fiderating: fiderating,
        fullname: `${m.last_name}, ${m.first_name}`,
        first_name: m.first_name,
        idnumber: m.idnumber,
        idcluborig: m.idclub,
        idclubvisit: 0,
        last_name: m.last_name,
        natrating: natrating,
        nature: pnature,
        period: pll_period,
        titular: "",
        transfer: null,
      }
      players.value.push(newplayer)
      playersindexed[m.idnumber] = newplayer
    }
  })
  players.value.forEach((p) => {
    let calrating = p.fiderating > 0 ? p.fiderating : p.natrating
    let mindiv = ""
    for (const [div, minelo] of Object.entries(icdata.max_elo)) {
      if (calrating <= minelo) {
        mindiv = div
      }
    }
    p.mindiv = mindiv
    p.fullname = `${p.last_name}, ${p.first_name}`
    if (
      p.assignedrating > 0 &&
      p.assignedrating < mininmal_assignelo &&
      p.period == "september"
    ) {
      mininmal_assignelo = p.assignedrating
    }
  })
}

async function getClubMembers() {
  // get club members for member database currently on old site
  if (!idclub.value) {
    clubmembers.value = []
    return
  }
  console.log("getting Club Members from signaletique")
  if (idclub.value == clubmembers_cache_idclub) {
    console.log("using cached version of members")
    return
  }
  showLoading(true)
  let reply
  clubmembers.value = []
  try {
    reply = await $backend("member", "anon_getclubmembers", {
      idclub: idclub.value,
    })
  } catch (error) {
    console.log("getClubMembers error")
    showSnackbar(error.message)
    return
  } finally {
    showLoading(false)
  }
  clubmembers_cache_idclub = idclub.value
  const members = reply.data
  members.forEach((p) => {
    p.merged = `${p.idnumber}: ${p.first_name} ${p.last_name}`
  })
  clubmembers.value = members.sort((a, b) => (a.last_name > b.last_name ? 1 : -1))
}

function maxelo(p) {
  if (pll_period == "september") {
    if (!p.fiderating && !p.natrating) return icdata.notrated_elo.max
    return p.fiderating ? Math.max(p.fiderating, p.natrating) + 100 : p.natrating + 100
  } else {
    return mininmal_assignelo - 1
  }
}

function minelo(p) {
  let minrating = p.fiderating
    ? Math.min(p.fiderating, p.natrating) - 100
    : p.natrating - 100
  return Math.max(minrating, icdata.notrated_elo.min)
}

function openAssignPlayer(idnumber) {
  playeredit.value = { ...playersindexed[idnumber] }
  assigndialog.value = true
}

function openEditElo(idnumber) {
  playeredit.value = { ...playersindexed[idnumber] }
  editelodialog.value = true
}

function openEditTitular(idnumber) {
  playeredit.value = { ...playersindexed[idnumber] }
  titnotit.value = playeredit.value.titular ? "tit" : "notit"
  edittitulardialog.value = true
}

function openTransferAll() {
  transferalldialog.value = true
}

function openTransferPlayer(idnumber) {
  playeredit.value = { ...playersindexed[idnumber] }
  transferdialog.value = true
}

function openUnassignPlayer(idnumber) {
  playeredit.value = { ...playersindexed[idnumber] }
  unassigndialog.value = true
}

function playerEdit2Player() {
  // copy the data of Player Edit back to the Player
  // we splice the players array and add the playeredit to trigger a repaint of the table
  const aix = players.value.findIndex((p) => p.idnumber == playeredit.value.idnumber)
  players.value.splice(aix, 1, playeredit.value)
  playersindexed[playeredit.value.idnumber] = players.value[aix]
}

function processAssignPlayer(idnumber) {
  playeredit.value.nature = PLAYERSTATUS.assigned
  playeredit.value.period = pll_period
  playerEdit2Player()
  assigndialog.value = false
}

function processEditElo() {
  playerEdit2Player()
  editelodialog.value = false
}

function processEditTitular() {
  if (titnotit.value == "notit") {
    playeredit.value.titular = ""
  }
  playerEdit2Player()
  edittitulardialog.value = false
}

function processTransferAll() {
  players.value.forEach((m) => {
    m.nature = PLAYERSTATUS.exported
    m.idclubvisit = parseInt(exportallvisit.value) + 0
  })
  transferalldialog.value = false
}

function processTransferPlayer() {
  playeredit.value.nature = PLAYERSTATUS.exported
  playeredit.value.idclubvisit = parseInt(playeredit.value.idclubvisit) + 0
  playerEdit2Player()
  transferdialog.value = false
}

function processUnassignPlayer() {
  playeredit.value.nature = PLAYERSTATUS.unassigned
  playerEdit2Player()
  unassigndialog.value = false
}

function readICclub() {
  idclub.value = icclub.value.idclub || 0
  registered.value = icclub.value.registered || false
  players.value = icclub.value.players ? [...icclub.value.players] : []
  playersindexed = Object.fromEntries(players.value.map((x) => [x.idnumber, x]))
  titularchoices.splice(1, titularchoices.length - 1)
  if (icclub.value.teams) {
    icclub.value.teams.forEach((t) => {
      titularchoices.push({ title: t.name, value: t.name })
    })
  }
}

function rowstyle(idnumber) {
  const pl = playersindexed[idnumber]
  if (!pl) return {}
  return {
    imported: pl.nature == "imported",
    exported: pl.nature == "exported",
    unassigned: pl.nature == "unassigned",
  }
}

async function savePlayerlist() {
  let reply
  try {
    showLoading(true)
    reply = await $backend("interclub", "clb_setICclub", {
      token: idtoken.value,
      idclub: idclub.value,
      players: players.value,
    })
  } catch (error) {
    showSnackbar(error.message)
    return
  } finally {
    showLoading(false)
  }
  validationdialog.value = false
  showSnackbar("Playerlist saved")
}

function visitingclub(idnumber) {
  const pl = playersindexed[idnumber]
  return pl ? pl.idclubvisit : ""
}

async function validatePlayerlist() {
  if (!registered.value) {
    savePlayerlist()
    return
  }
  let reply
  try {
    showLoading(true)
    reply = await $backend("interclub", "clb_validateICplayers", {
      token: idtoken.value,
      idclub: idclub.value,
      players: players.value,
    })
  } catch (error) {
    showSnackbar(error.message)
    return
  } finally {
    showLoading(false)
  }
  console.log("reply.data", reply.data)
  validationerrors.value = reply.data
  if (validationerrors.value.length) {
    validationdialog.value = true
  } else {
    savePlayerlist()
  }
}

async function setup(icclub_, icdata_) {
  console.log("setup playerlist", icclub_, icdata_)
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  icclub.value = icclub_
  idclub.value = icclub_.idclub || 0
  if (icdata_.playerlist_data) {
    icdata = icdata_
    calc_period()
    await calc_status()
    readICclub()
    await getClubMembers()
  }
}
</script>

<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <v-alert
      type="warning"
      variant="outlined"
      v-if="pll_status == 'closed'"
      :text="t('icn.pll_closed')"
    />
    <v-alert
      type="warning"
      variant="outlined"
      v-if="pll_status == 'noclub'"
      :text="t('icn.select_club')"
    />
    <v-alert
      type="error"
      variant="outlined"
      v-if="pll_status == 'noaccess'"
      :text="t('icn.perm_denied')"
    />
    <div v-if="pll_status == 'open'">
      <div v-if="!registered">
        This club is not enrolled in Interclubs 2025-26
        <VBtn @click="openTransferAll" color="primary" class="ml-8">
          Export all players
        </VBtn>
      </div>
      <div v-if="!players.length" class="mb-3">
        The current playerlist is empty. Do you want to import the club members?
        <VBtn @click="fillinPlayerList" color="primary" class="ml-8">
          Import members
        </VBtn>
      </div>
      <VDataTable
        class="playerlist"
        :items="players"
        :headers="headers"
        density="compact"
        :items-per-page="itemsPerPage"
        :items-per-page-options="itemsPerPageOptions"
        :sort-by="[{ key: 'assignedrating', order: 'desc' }]"
      >
        <template v-slot:item.index="{ item, index }">
          <span :class="rowstyle(item.idnumber)">
            {{ index + 1 }}
          </span>
        </template>

        <template v-slot:item.fullname="{ item }">
          <span :class="rowstyle(item.idnumber)">
            {{ item.last_name }}, {{ item.first_name }}
          </span>
        </template>

        <template v-slot:item.idnumber="{ item }">
          <span :class="rowstyle(item.idnumber)">
            {{ item.idnumber }}
          </span>
        </template>

        <template v-slot:item.assignedrating="{ item }">
          <span :class="rowstyle(item.idnumber)">
            {{ item.assignedrating }}
          </span>
        </template>

        <template v-slot:item.idclub="{ item }">
          <span :class="rowstyle(item.idnumber)">
            {{ item.idclub }}
          </span>
        </template>

        <template v-slot:item.action="{ item }">
          <v-menu>
            <template v-slot:activator="{ props }">
              <VBtn
                density="compact"
                icon="mdi-dots-vertical"
                variant="text"
                v-bind="props"
              />
            </template>
            <v-list>
              <v-list-item
                @click="openEditElo(item.idnumber)"
                v-show="canEditElo(item.idnumber)"
              >
                <v-list-item-title>Edit Elo</v-list-item-title></v-list-item
              >
              <v-list-item
                @click="openEditTitular(item.idnumber)"
                v-show="canEditTitular(item.idnumber)"
              >
                <v-list-item-title>Edit Titular</v-list-item-title></v-list-item
              >
              <v-list-item
                @click="openUnassignPlayer(item.idnumber)"
                v-show="canUnassign(item.idnumber)"
                ><v-list-item-title
                  >Remove from playerlist</v-list-item-title
                ></v-list-item
              >
              <v-list-item
                @click="openAssignPlayer(item.idnumber)"
                v-show="canAssign(item.idnumber)"
              >
                <v-list-item-title>Add to playerlist</v-list-item-title></v-list-item
              >
              <v-list-item
                @click="openTransferPlayer(item.idnumber)"
                v-show="canExport(item.idnumber)"
                ><v-list-item-title>Transfer</v-list-item-title></v-list-item
              >
            </v-list>
          </v-menu>
          <span class="red" v-show="item.nature == 'exported'">
            <v-icon icon="mdi-arrow-right" />
            {{ item.idclubvisit }}
          </span>
        </template>
      </VDataTable>
      <div>
        <VBtn @click="validatePlayerlist()" color="primary">Save</VBtn>
      </div>
    </div>

    <VDialog v-model="assigndialog" width="30em">
      <VCard>
        <VCardTitle>
          {{ playeredit.last_name }}, {{ playeredit.first_name }}
          <VDivider />
        </VCardTitle>
        <VCardText>
          <p>Assign a player to the playerlist</p>
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn @click="processAssignPlayer">OK</VBtn>
          <VBtn @click="assigndialog = false">Cancel</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>

    <VDialog v-model="editelodialog" width="30em">
      <VCard>
        <VCardTitle>
          {{ t("Edit") }}: {{ playeredit.first_name }} {{ playeredit.last_name }}
          <v-divider class="divider" />
        </VCardTitle>
        <VCardText>
          <h4>{{ t("icn.pll_edit_assigned") }}</h4>
          <div>{{ t("icn.pll_assigned_elo") }}: {{ playeredit.assignedrating }}</div>
          <div>Max ELO: {{ maxelo(playeredit) }}</div>
          <div>Min ELO: {{ minelo(playeredit) }}</div>
          <VTextField v-model="playeredit.assignedrating" label="New Elo" />
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn @click="processEditElo">{{ t("OK") }}</VBtn>
          <VBtn @click="editelodialog = false">{{ t("Cancel") }}</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>

    <VDialog v-model="edittitulardialog" width="30em">
      <VCard>
        <VCardTitle>
          {{ t("Edit") }}: {{ playeredit.first_name }} {{ playeredit.last_name }}
          <v-divider class="divider" />
        </VCardTitle>
        <VCardText>
          <h4>{{ t("Titular") }}</h4>
          <v-radio-group v-model="titnotit">
            <v-radio :label="t('icn.pll_notit')" value="notit"></v-radio>
            <v-radio :label="t('icn.pll_tit')" value="tit"></v-radio>
          </v-radio-group>
          <VSelect
            :items="titularchoices"
            v-model="playeredit.titular"
            v-show="titnotit == 'tit'"
          ></VSelect>
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn @click="processEditTitular">{{ t("OK") }}</VBtn>
          <VBtn @click="edittitulardialog = false">{{ t("Cancel") }}</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>

    <VDialog v-model="transferdialog" width="30em">
      <VCard>
        <VCardTitle>
          Export: {{ playeredit.last_name }}, {{ playeredit.first_name }}
          <VDivider />
        </VCardTitle>
        <VCardText>
          <p>Exporting a player to another club</p>
          <VTextField label="Club number" v-model="playeredit.idclubvisit" />
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn @click="processTransferPlayer">OK</VBtn>
          <VBtn @click="transferdialog = false">Cancel</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>

    <VDialog v-model="unassigndialog" width="30em">
      <VCard>
        <VCardTitle>
          {{ playeredit.last_name }}, {{ playeredit.first_name }}
          <VDivider />
        </VCardTitle>
        <VCardText>
          <p>Removing a player from the playerlist</p>
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn @click="processUnassignPlayer">OK</VBtn>
          <VBtn @click="unassigndialog = false">Cancel</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>

    <VDialog v-model="transferalldialog" width="30em">
      <VCard>
        <VCardTitle>
          Export all players
          <VDivider />
        </VCardTitle>
        <VCardText>
          <p>Exporting all players to another club</p>
          <VTextField label="Club number" v-model="exportallvisit" />
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn @click="processTransferAll">OK</VBtn>
          <VBtn @click="transferalldialog = false">Cancel</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>

    <VDialog v-model="validationdialog" width="30em">
      <VCard>
        <VCardTitle>
          {{ t("Validation of player list.") }}
          <VDivider />
        </VCardTitle>
        <VCardText class="markdowncontent">
          <div>{{ t("The player list contains validation errors") }}</div>
          <ul>
            <li v-for="(err, ix) in validationerrors" :key="ix">
              <span v-show="err.errortype == 'ELO'">
                {{ t("Player") }} {{ t(err.detail) }}: {{ t(err.message) }}
              </span>
              <span v-show="err.errortype == 'TitularOrder'">
                {{ t(err.message) }}
              </span>
              <span v-show="err.errortype == 'TitularCount'">
                {{ t(err.detail) }}: {{ t(err.message) }}
              </span>
            </li>
          </ul>
          <VDivider />
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn @click="savePlayerlist()">{{ t("Save anyhow") }}</VBtn>
          <VBtn @click="validationdialog = false">{{ t("Cancel") }}</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>
  </v-container>
</template>

<style scoped>
.divider {
  margin: 1em 0;
  color: darkseagreen;
}
.imported {
  color: purple;
  font-weight: 500;
}

.exported {
  color: rgb(186, 185, 185);
}

.unassigned {
  color: rgb(195, 195, 195);
}
</style>

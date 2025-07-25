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
const clubmembers = ref([])
const clubmembers_id = ref(null)
const icclub = ref({})
const idclub = ref(0)
const registered = ref(null)
let playersindexed = {}
const players = ref([])
const playeredit = ref({})
const editdialog = ref(false)
const exportalldialog = ref(false)
const exportallvisit = ref(0)
const exportdialog = ref(false)
const titularchoices = [{ title: "No titular", value: "" }]
const pll_status = ref("closed")
let pll_period
let pll_startdate
let pll_enddate
let mininmal_assignelo = 3000
let icdata = {}

// validation
const validationdialog = ref(false)
const validationerrors = ref([])

// data table definiton
const headers = [
  { title: "N", key: "index" },
  { title: "Name", key: "fullname" },
  { title: "ID number", key: "idnumber", sortable: false },
  { title: "ELO", key: "assignedrating" },
  { title: "F-ELO", key: "fiderating" },
  { title: "B-ELO", key: "natrating" },
  { title: "Club", key: "idcluborig" },
  { title: "Titular", key: "titular" },
  { title: "Min div", key: "mindiv" },
  { title: "Period", key: "period" },
  { title: "Actions", key: "action" },
]
const itemsPerPage = 50
const itemsPerPageOptions = [
  { value: 50, title: "50" },
  { value: 150, title: "150" },
  { value: -1, title: "All" },
]

// methods alphabetically

function assignPlayer(idnumber) {
  console.log("Assigning player", idnumber)
  playeredit.value = { ...playersindexed[idnumber] }
  playeredit.value.nature = PLAYERSTATUS.assigned
  playeredit.value.period = pll_period
  playerEdit2Player()
}

function calcstatus() {
  console.log("calcstatus")
  // we have the following status
  // - open
  // - closed
  // - noclub
  // - noaccess
  if (!icclub.value.idclub) {
    pll_status.value = "noclub"
    return
  }
  pll_status.value = "open"
}

function canAssign(idnumber) {
  return (
    [PLAYERSTATUS.unassigned].includes(playersindexed[idnumber].nature) &&
    !playersindexed[idnumber].natrating &&
    !playersindexed[idnumber].fiderating
  )
}

function canEdit(idnumber) {
  return [PLAYERSTATUS.assigned, PLAYERSTATUS.unassigned, PLAYERSTATUS.imported].includes(
    playersindexed[idnumber].nature
  )
}

function canExport(idnumber) {
  console.log("canExport", playersindexed[idnumber].nature)
  return [PLAYERSTATUS.assigned, PLAYERSTATUS.unassigned].includes(
    playersindexed[idnumber].nature
  )
}

function doEditPlayer() {
  playerEdit2Player()
  editdialog.value = false
}

function doExportAll() {
  players.value.forEach((m) => {
    m.nature = PLAYERSTATUS.confirmedout
    m.idclubvisit = parseInt(exportallvisit.value) + 0
  })
  exportalldialog.value = false
}

function doExportPlayer() {
  playeredit.value.nature = PLAYERSTATUS.exported
  playeredit.value.idclubvisit = parseInt(playeredit.value.idclubvisit) + 0
  playerEdit2Player()
  exportdialog.value = false
}

function fillinPlayerList() {
  // add new members to the playerlist
  console.log("fillinPlayerList")
  pll_period = "unknown"
  const now = new Date()
  icdata.playerlist_data.forEach((p) => {
    let start = new Date(p.start)
    let end = new Date(p.end)
    if (now.valueOf() > start.valueOf() && now.valueOf() < end.valueOf()) {
      pll_status.value = "open"
      pll_period = p.period
      pll_startdate = p.start
      pll_enddate = p.end
      return
    }
  })
  console.log("pll_period", pll_period)
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
      m.fiderating = m.fiderating || 0
      let calcrating = m.fiderating > 0 ? m.fiderating : m.natrating
      let newplayer = {
        assignedrating: calcrating,
        fiderating: m.fiderating,
        fullname: `${m.last_name}, ${m.first_name}`,
        first_name: m.first_name,
        idnumber: m.idnumber,
        idcluborig: m.idclub,
        idclubvisit: 0,
        last_name: m.last_name,
        natrating: m.natrating,
        nature: pnature,
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
  if (idclub.value == clubmembers_id.value) {
    console.log("using cached version of members")
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
  clubmembers_id.value = idclub.value
  const members = reply.data
  members.forEach((p) => {
    p.merged = `${p.idnumber}: ${p.first_name} ${p.last_name}`
  })
  clubmembers.value = members.sort((a, b) => (a.last_name > b.last_name ? 1 : -1))
  fillinPlayerList()
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

function openEditPlayer(idnumber) {
  playeredit.value = { ...playersindexed[idnumber] }
  editdialog.value = true
}

function openExportAll() {
  exportalldialog.value = true
}

function openExportPlayer(idnumber) {
  playeredit.value = { ...playersindexed[idnumber] }
  exportdialog.value = true
}

function playerEdit2Player() {
  // copy the data of Player Edit back to the Player
  // we splice the players array and add the playeredit to trigger a repaint of the table
  const aix = players.value.findIndex((p) => p.idnumber == playeredit.value.idnumber)
  players.value.splice(aix, 1, playeredit.value)
  playersindexed[playeredit.value.idnumber] = players.value[aix]
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
  fillinPlayerList()
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
    reply = await $backend("interclub", "mgmt_setICclub", {
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
    reply = await $backend("interclub", "mgmt_validateICplayers", {
      token: idtoken.value,
      idclub: idclub.value,
      players: players.value,
    })
  } catch (error) {
    console.error("failed validate", error)
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
  icdata = icdata_
  calcstatus()
  readICclub()
  getClubMembers()
}
</script>

<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />

    <v-alert
      type="warning"
      variant="outlined"
      v-if="pll_status == 'noclub'"
      text="Select club"
    />
    <div v-if="pll_status == 'open'">
      <div v-if="!registered">
        This club is not registered for Interclubs 2025-26
        <VBtn @click="openExportAll" color="primary" class="ml-8">
          Export all players
        </VBtn>
      </div>
      <VDataTable
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
            {{ item.fullname }}
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
          <span v-show="item.nature == 'exported'">
            <VIcon>mdi-arrow-right-bold</VIcon>{{ visitingclub(item.idnumber) }}
          </span>
          <VBtn
            density="compact"
            color="green"
            icon="mdi-pencil"
            variant="text"
            v-show="canEdit(item.idnumber)"
            @click="openEditPlayer(item.idnumber)"
          />
          <VBtn
            density="compact"
            color="red"
            icon="mdi-arrow-right"
            variant="text"
            v-show="canExport(item.idnumber)"
            @click="openExportPlayer(item.idnumber)"
          />
          <VBtn
            density="compact"
            color="blue"
            icon="mdi-clipboard-arrow-down"
            variant="text"
            v-show="canAssign(item.idnumber)"
            @click="assignPlayer(item.idnumber)"
          />
        </template>
      </VDataTable>
      <div>
        <VBtn @click="validatePlayerlist()" color="primary">Save</VBtn>
      </div>
    </div>
    <VDialog v-model="editdialog" width="30em">
      <VCard>
        <VCardTitle>
          Edit: {{ playeredit.fullname }}
          <v-divider class="divider" />
        </VCardTitle>
        <VCardText>
          <h4>Modify assigned Elo</h4>
          <div>Current assigned rating: {{ playeredit.assignedrating }}</div>
          <div>Max ELO: {{ maxelo(playeredit) }}</div>
          <div>Min ELO: {{ minelo(playeredit) }}</div>
          <VTextField v-model="playeredit.assignedrating" label="New Elo" />
          <h4>Titular</h4>
          <VSelect :items="titularchoices" v-model="playeredit.titular"></VSelect>
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn @click="doEditPlayer">OK</VBtn>
          <VBtn @click="editdialog = false">Cancel</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>
    <VDialog v-model="exportdialog" width="30em">
      <VCard>
        <VCardTitle>
          Export: {{ playeredit.fullname }}
          <VDivider />
        </VCardTitle>
        <VCardText>
          <p>Exporting a player to another club</p>
          <VTextField label="Club number" v-model="playeredit.idclubvisit" />
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn @click="doExportPlayer">OK</VBtn>
          <VBtn @click="exportdialog = false">Cancel</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>
    <VDialog v-model="exportalldialog" width="30em">
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
          <VBtn @click="doExportAll">OK</VBtn>
          <VBtn @click="exportalldialog = false">Cancel</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>
    <VDialog v-model="validationdialog" width="30em">
      <VCard>
        <VCardTitle>
          Validation of player list.
          <VDivider />
        </VCardTitle>
        <VCardText class="markdowncontent">
          <div>The player list contains validation errors</div>
          <ul>
            <li v-for="(err, ix) in validationerrors" :key="ix">
              <span v-show="err.errortype == 'ELO'">
                Player {{ err.detail }}: {{ err.message }}
              </span>
              <span v-show="err.errortype == 'TitularCount'">
                {{ err.detail }}: {{ err.message }}
              </span>
            </li>
          </ul>
          <VDivider />
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn @click="savePlayerlist()">Save anyhow</VBtn>
          <VBtn @click="validationdialog = false">Cancel</VBtn>
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
  color: rgb(109, 123, 183);
}
</style>

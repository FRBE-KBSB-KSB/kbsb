<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useIdtokenStore } from '@/store/idtoken'
import { storeToRefs } from 'pinia'

// communication
defineExpose({ setup })
const idstore = useIdtokenStore()
const { token: idtoken } = storeToRefs(idstore)
const { $backend } = useNuxtApp()
const { t } = useI18n()

//  snackbar and loading widgets
import ProgressLoading from '@/components/ProgressLoading.vue'
import SnackbarMessage from '@/components/SnackbarMessage.vue'
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

let icdata = {}


// validation
const validationdialog = ref(false)
const validationerrors = ref([])

// data table definiton
const headers = [
  { title: "N", key: "index" },
  { title: t("Name"), key: 'fullname' },
  { title: t("ID number"), key: 'idnumber', sortable: false },
  { title: "ELO", key: "assignedrating" },
  { title: "F-ELO", key: "fiderating" },
  { title: "B-ELO", key: "natrating" },
  { title: "Club", key: "idcluborig" },
  { title: t("Titular"), key: "titular" },
  { title: t("Min div"), key: "mindiv" },
  { title: t("Actions"), key: "action" },
]
const itemsPerPage = 50
const itemsPerPageOptions = [
  { value: 50, title: '50' },
  { value: 150, title: '150' },
  { value: -1, title: 'All' }
]

// methods alphabetically

function assignPlayer(idnumber) {
  console.log('Assigning player', idnumber)
  playeredit.value = { ...playersindexed[idnumber] }
  playeredit.value.nature = PLAYERSTATUS.assigned
  playerEdit2Player()
}

function calcstatus(){
  // we have the following status
  // - open
  // - closed
  // - noclub
  // - noaccess
  
  if (!idclub.value) {
    pll_status.value = 'noclub'
    return
  }
  pll_status.value = 'closed'
  const now = new Date()
  icdata.playerlist_data.forEach(p => {
    let start = new Date(p.start)
    let end = new Date(p.end)
    console.log('now', now, 'start', start, 'end', end)
    if (now.valueOf() > start.valueOf() && now.valueOf() < end.valueOf()) {
      pll_status.value = 'open'
      pll_period = p.period
      pll_startdate = p.start
      pll_enddate = p.end
      return
    }
  })

}

function canAssign(idnumber) {
  return [PLAYERSTATUS.unassigned].includes(playersindexed[idnumber].nature) &&
    (!playersindexed[idnumber].natrating) &&
    (!playersindexed[idnumber].fiderating)
}

function canEdit(idnumber) {
  return [PLAYERSTATUS.assigned, PLAYERSTATUS.comfirmedin, PLAYERSTATUS.requestedin].includes(
    playersindexed[idnumber].nature)
}


function canExport(idnumber) {
  return [PLAYERSTATUS.assigned, PLAYERSTATUS.unassiged].includes(
    playersindexed[idnumber].nature)
}

async function checkAccess() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("club", "verify_club_access", {
      idclub: icclub.idclub,
      role: "InterclubAdmin,InterclubCaptain",
      token: idtoken.value,
    })
    return true
  } catch (error) {
    console.log('reply NOK', error)
    enr_status.value = 'noaccess'
    showSnackbar(t('icn.perm_denied'))
    return false
  } finally {
    showLoading(false)
  }
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
  playeredit.value.nature = PLAYERSTATUS.confirmedout
  playeredit.value.idclubvisit = parseInt(playeredit.value.idclubvisit) + 0
  playerEdit2Player()
  exportdialog.value = false
}

function fillinPlayerList() {
  // add new members to the playerlist
  let pnature = PLAYERSTATUS.unassigned
  const now = new Date().valueOf()
  if (registered.value) {
    // automatically make players assigned at the start of the Interclubs
    pnature = PLAYERSTATUS.assigned
  }
  clubmembers.value.forEach((m) => {
    if (!playersindexed[m.idnumber]) {
      m.fiderating = m.fiderating || 0 
      let usedrating = m.fiderating > 0 ? m.fiderating: m.natrating
      let mindiv = ""
      for (const [div, minelo] of Object.entries(icdata.max_elo)) {
         if (usedrating <= minelo) {
          mindiv = div
        }
      }
      let newplayer = {
        assignedrating: usedrating,
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
        mindiv: mindiv,
        transfer: null,
      }
      players.value.push(newplayer)
      playersindexed[m.idnumber] = newplayer
    }
  })
  players.value.forEach((p) => {
    if (!p.fullname) {
      p.fullname = `${p.last_name}, ${p.first_name}`
    }
  })
}

async function getClubMembers() {
  // get club members for member database currently on old site
  if (!idclub.value) {
    clubmembers.value = []
    return
  }
  console.log('getting Club Members from signaletique')
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
    console.log('getClubMembers error')
    showSnackbar(error.message)
    return
  } finally {
    showLoading(false)
  }
  clubmembers_id.value = idclub.value
  const members = reply.data
  members.forEach(p => {
    p.merged = `${p.idnumber}: ${p.first_name} ${p.last_name}`
  })
  clubmembers.value = members.sort((a, b) =>
    (a.last_name > b.last_name ? 1 : -1))
  fillinPlayerList()
}

function maxelo(p) {
  if (!p.fiderating && !p.natrating) return 1600
  return p.fiderating ? Math.max(p.fiderating, p.natrating) + 100 : p.natrating + 100
}

function minelo(p) {
  let minrating = p.fiderating ? Math.min(p.fiderating, p.natrating) - 100 : p.natrating - 100
  return Math.max(minrating, 1000)
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
    imported: pl.nature == "requestedin",
    exported: pl.nature == "confirmedout",
    unassigned: pl.nature == "unassigned"
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
  }
  finally {
    showLoading(false)
  }
  validationdialog.value = false
  showSnackbar('Playerlist saved')
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
  }
  finally {
    showLoading(false)
  }
  console.log('reply.data', reply.data)
  validationerrors.value = reply.data
  if (validationerrors.value.length) {
    validationdialog.value = true
  }
  else {
    savePlayerlist()
  }

}

async function setup(icclub_, icdata_) {
  console.log('setup playerlist', icclub_, icdata_)
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading  
  icclub.value = icclub_
  icdata = icdata_
  readICclub()
  calcstatus()
  getClubMembers()
}

</script>

<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <v-alert type="warning" variant="outlined" v-if="pll_status == 'closed'"
      :text="t('icn.pll_closed')" />
    <v-alert type="warning" variant="outlined" v-if="pll_status == 'noclub'"
      :text="t('icn.select_club')" />
    <v-alert type="error" variant="outlined" v-if="pll_status == 'noaccess'"
      :text="t('icn.perm_denied')" />  
    <div v-if="pll_status == 'open'">
      <div v-if="!registered">
        This club is not enrolled in Interclubs 2023-24
        <VBtn @click="openExportAll" color="primary" class="ml-8">
          Export all players
        </VBtn>
      </div>
      <VDataTable :items="players" :headers="headers" density="compact"
        :items-per-page="itemsPerPage" :items-per-page-options="itemsPerPageOptions"
        :sort-by="[{ key: 'assignedrating', order: 'desc' }]">
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
          <span v-show="item.nature == 'confirmedout'">
            <VIcon>mdi-arrow-right-bold</VIcon>{{ visitingclub(item.idnumber) }}
          </span>
          <VBtn density="compact" color="green" icon="mdi-pencil" variant="text"
            v-show="canEdit(item.idnumber)" @click="openEditPlayer(item.idnumber)" />
          <VBtn density="compact" color="red" icon="mdi-arrow-right" variant="text"
            v-show="canExport(item.idnumber)" @click="openExportPlayer(item.idnumber)" />
          <VBtn density="compact" color="green" icon="mdi-arrow-left" variant="text"
            v-show="canAssign(item.idnumber)" @click="assignPlayer(item.idnumber)" />
        </template>
      </VDataTable>
      <div>
        <VBtn @click="validatePlayerlist()" color="primary">Save</VBtn>
      </div>
    </div>
    <VDialog v-model="editdialog" width="30em">
      <VCard>
        <VCardTitle>
          {{ t('Edit') }}: {{ playeredit.fullname }}
          <v-divider class="divider" />
        </VCardTitle>
        <VCardText>
          <h4>{{ t('Modify assigned Elo') }}</h4>
          <div>{{ t('Current assigned rating') }}: {{ playeredit.assignedrating }} </div>
          <div>Max ELO: {{ maxelo(playeredit) }}</div>
          <div>Min ELO: {{ minelo(playeredit) }}</div>
          <VTextField v-model="playeredit.assignedrating" label="New Elo" />
					<h4>{{ t('Titular') }}</h4>
						<VSelect :items="titularchoices" v-model="playeredit.titular"></VSelect>
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn @click="doEditPlayer">{{ t('OK') }}</VBtn>
          <VBtn @click="editdialog = false">{{ t('Cancel') }}</VBtn>
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
          {{ t('Validation of player list.') }}
          <VDivider />
        </VCardTitle>
        <VCardText class="markdowncontent">
          <div>{{ t('The player list contains validation errors') }}</div>
          <ul>
            <li v-for="(err, ix) in validationerrors" :key="ix">
              <span v-show="err.errortype == 'ELO'">
                {{ t('Player') }} {{ t(err.detail) }}: {{ t(err.message) }}
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
          <VBtn @click="savePlayerlist()">{{ t('Save anyhow') }}</VBtn>
          <VBtn @click="validationdialog = false">{{ t('Cancel') }}</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>
  </v-container>
</template>

<style scoped>
.divider {
  margin: 1em 0;
  color:darkseagreen
}
.imported {
  color: purple;
  font-weight: 500;
}

.exported,
.unassigned {
  color: rgb(186, 185, 185);
}
</style>

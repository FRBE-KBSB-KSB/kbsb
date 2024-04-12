<script setup>
import { ref, computed, nextTick } from 'vue'
import { PLAYERSTATUS } from "@/util/interclubs"

// stores
import { useMgmtTokenStore } from "@/store/mgmttoken"
import { useMgmtInterclubStore } from "@/store/mgmtinterclub"
import { storeToRefs } from 'pinia'
const mgmttokenstore = useMgmtTokenStore()
const { token: mgmttoken } = storeToRefs(mgmttokenstore)
const mgmtinterclubstore = useMgmtInterclubStore()
const { club, round } = storeToRefs(mgmtinterclubstore)

// communication
defineExpose({ checkStore })
const { $backend } = useNuxtApp()

//  snackbar and loading widgets
import ProgressLoading from '@/components/ProgressLoading.vue'
import SnackbarMessage from '@/components/SnackbarMessage.vue'
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading
const showPlayerlist = ref(false)

// datamodel
const my = {
  idclub: 0,
  round: 0
}
const clubmembers = ref([])
const enrolled = ref(null)
let playersindexed = {}
const players = ref([])
const playeredit = ref({})
const editdialog = ref(false)
const exportalldialog = ref(false)
const exportallvisit = ref(0)
const exportdialog = ref(false)
const titularchoices = [{ title: "No titular", value: "" }]

// validation
const validationdialog = ref(false)
const validationerrors = ref([])

// data table definiton
const headers = [
  { title: "N", key: "index" },
  { title: "Name", key: 'fullname' },
  { title: "ID number", key: 'idbel', sortable: false },
  { title: "ELO", key: "assignedrating" },
  { title: "F-ELO", key: "fiderating" },
  { title: "B-ELO", key: "natrating" },
  { title: "Club", key: "idcluborig" },
  { title: "Titular", key: "titular" },
  { title: "Status", key: "nature" },
  { title: "Actions", key: "action" },
]
const itemsPerPage = 50
const itemsPerPageOptions = [
  { value: 50, title: '50' },
  { value: 150, title: '150' },
  { value: -1, title: 'All' }
]

// Constants changing per year
const startdate1 = "2023-09-01"
const cutoffday1 = "2023-09-18"
const startdate2 = "2023-10-28"
const cutoffday2 = "2023-11-04"
const startdate3 = "2023-12-28"
const cutoffday3 = "2024-01-04"

// methods alphabetically

function assignPlayer(idbel) {
  console.log('Assigning player', idbel)
  playeredit.value = { ...playersindexed[idbel] }
  playeredit.value.nature = PLAYERSTATUS.assigned
  playerEdit2Player()
}

function canAssign(idbel) {
  return [PLAYERSTATUS.unassigned].includes(
    playersindexed[idbel].nature)
}

function canEdit(idbel) {
  if (!playersindexed[idbel]) {
    console.log('idbel not in playersindexed', idbel)
  }
  return [PLAYERSTATUS.assigned, PLAYERSTATUS.comfirmedin, PLAYERSTATUS.requestedin].includes(
    playersindexed[idbel].nature)
}

function canExport(idbel) {
  return [PLAYERSTATUS.assigned, PLAYERSTATUS.unassiged].includes(
    playersindexed[idbel].nature)
}

async function checkStore() {
  console.log('checkStore playerlist')
  if (my.idclub != club.value.idclub) {
    // change detected
    my.idclub = club.value.idclub
    showPlayerlist.value = !!my.idclub
    await nextTick()
    if (my.idclub) {
      readICclub()
      await getClubMembers()
      if (players.value.length) {
        fillinPlayerList()
      }
    }
    else {
      players.value = []
      playersindexed = {}
    }
  }
}

function compareLastName(a, b) {
  if (a.last_name > b.last_name) return 1
  if (a.last_name < b.last_name) return -1
  return 0
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
  console.log('filling playerlist clubmembers', clubmembers.value)
  let assigning = [], existass
  clubmembers.value.forEach((m) => {
    let maxrating = Math.max(m.fiderating, m.natrating)
    let newplayer = {
      assignedrating: maxrating,
      date_affiliation: m.date_affiliation,
      fiderating: m.fiderating,
      fullname: `${m.last_name}, ${m.first_name}`,
      first_name: m.first_name,
      idbel: m.idbel,
      idcluborig: m.idclub,
      idclubvisit: 0,
      last_name: m.last_name,
      natrating: m.natrating,
      nature: maxrating ? PLAYERSTATUS.unassigned : PLAYERSTATUS.assigned,
      titular: "",
      transfer: null,
    }
    let existpl = playersindexed[newplayer.idbel]
    if (existpl) {
      if (!maxrating && existpl.nature == PLAYERSTATUS.unassigned) {
        // flagging a reassign
        console.log('adding for reassigning', newplayer.idbel)
        newplayer.reassign = true
        playersindexed[newplayer.idbel] = newplayer
        assigning.push(newplayer)
      }
    }
    else {
      if (maxrating) {
        // stotre unassigned nature
        console.log('store unassgined rating', newplayer.idbel)
        playersindexed[newplayer.idbel] = newplayer
      }
      else {
        console.log('adding for assigning', newplayer.idbel)
        playersindexed[newplayer.idbel] = newplayer
        assigning.push(newplayer)
        // adding 
      }
    }
  })
  console.log('assigning', assigning)
  if (assigning.length) {
    assigning.sort(compareLastName)
    console.log('assigning sorted', assigning)
    existass = players.value.filter((p) =>
      [PLAYERSTATUS.assigned, PLAYERSTATUS.requestedin].includes(p.nature)
    )
    let minelo = 1150
    if (existass.length) {
      minelo = (existass.reduce((prev, curr) =>
        prev.assignedrating < curr.assignedrating ? prev : curr).assignedrating
      )
    }
    console.log('minelo', minelo)
    assigning.forEach((m) => {
      m.assignedrating = --minelo
      m.idnumber = m.idbel
      playersindexed[m.idbel] = m
      if (m.reassign) {
        // overwrite the existing player  
        const aix = players.value.findIndex((p) => p.idbel == m.idbel)
        players.value.splice(aix, 1, m)
      }
      else {
        // add it to the bottom
        players.value.push(m)
      }
    })
  }
  players.value.forEach((p) => {
    if (!p.fullname) {
      p.fullname = `${p.last_name}, ${p.first_name}`
    }
  })
}

async function getClubMembers() {
  let reply, cutoff
  console.log('getClubMembers', my.idclub)
  // get club members for member database currently on old site
  if (!my.idclub) {
    clubmembers.value = []
    return
  }
  const now = new Date().valueOf()
  showLoading(true)
  clubmembers.value = []
  try {
    reply = await $backend("member", "mgmt_getclubmembers", {
      token: mgmttoken.value,
      idclub: my.idclub,
    })
  } catch (error) {
    console.log('getClubMembers error')
    showSnackbar(error.message)
    return
  } finally {
    showLoading(false)
  }
  cutoff = new Date(cutoffday3).getTime()
  const members = reply.data.filter((m) =>
    cutoff > new Date(m.date_affiliation).getTime()
  )
  members.forEach(p => {
    p.merged = `${p.idbel}: ${p.first_name} ${p.last_name}`
  })
  clubmembers.value = members.sort((a, b) =>
    (a.last_name > b.last_name ? 1 : -1))
  console.log('clubmembers', clubmembers.value.length)
}

function minelo(p) {
  let minrating = p.fiderating ? Math.min(p.fiderating, p.natrating) - 100 : p.natrating - 100
  return Math.max(minrating, 1000)
}

function openEditPlayer(idbel) {
  playeredit.value = { ...playersindexed[idbel] }
  editdialog.value = true
}

function openExportAll() {
  exportalldialog.value = true
}

function openExportPlayer(idbel) {
  playeredit.value = { ...playersindexed[idbel] }
  exportdialog.value = true
}

function playerEdit2Player() {
  // copy the data of Player Edit back to the Player
  // we splice the players array and add the playeredit to trigger a repaint of the table
  const aix = players.value.findIndex((p) => p.idbel == playeredit.value.idbel)
  players.value.splice(aix, 1, playeredit.value)
  playersindexed[playeredit.value.idbel] = players.value[aix]
}

function readICclub() {
  enrolled.value = club.value.enrolled
  players.value = club.value.players ? [...club.value.players] : []
  players.value.forEach((m) => m.idbel = m.idnumber)
  playersindexed = Object.fromEntries(players.value.map((x) => [x.idbel, x]))
  titularchoices.splice(1, titularchoices.length - 1)
  if (club.value.teams) {
    club.value.teams.forEach((t) => {
      titularchoices.push({ title: t.name, value: t.name })
    })
  }
}

function rowstyle(idbel) {
  const pl = playersindexed[idbel]
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
    reply = await $backend("interclub", "mgmt_setICclub", {
      token: mgmttoken.value,
      idclub: my.idclub,
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

function status(idbel) {
  const pl = playersindexed[idbel]
  return pl ? pl.idclubvisit : ""
}

async function validatePlayerlist() {
  if (!enrolled.value) {
    savePlayerlist()
    return
  }
  let reply
  try {
    showLoading(true)
    reply = await $backend("interclub", "mgmt_validateICplayers", {
      token: mgmttoken.value,
      idclub: my.idclub,
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

onMounted(() => {
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
})

</script>
<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <h2>Player list</h2>
    <p v-show="!showPlayerlist">Please select a club to view the interclubs player list</p>
    <div v-show="showPlayerlist">
      <div v-if="enrolled">
        This club is enrolled in Interclubs 2023-24
      </div>
      <div v-else>
        This club is not enrolled in Interclubs 2023-24
        <VBtn @click="openExportAll" color="primary" class="ml-8">
          Export all players
        </VBtn>
      </div>
      <VDataTable :items="players" :headers="headers" density="compact"
        :items-per-page="itemsPerPage" :items-per-page-options="itemsPerPageOptions"
        :sort-by="[{ key: 'assignedrating', order: 'desc' }]">
        <template v-slot:item.index="{ item, index }">
          <span :class="rowstyle(item.idbel)">
            {{ index + 1 }}
          </span>
        </template>
        <template v-slot:item.fullname="{ item }">
          <span :class="rowstyle(item.idbel)">
            {{ item.fullname }}
          </span>
        </template>
        <template v-slot:item.idbel="{ item }">
          <span :class="rowstyle(item.idbel)">
            {{ item.idbel }}
          </span>
        </template>
        <template v-slot:item.assignedrating="{ item }">
          <span :class="rowstyle(item.idbel)">
            {{ item.assignedrating }}
          </span>
        </template>
        <template v-slot:item.idclub="{ item }">
          <span :class="rowstyle(item.idbel)">
            {{ item.idclub }}
          </span>
        </template>
        <template v-slot:item.nature="{ item }">
          <span v-show="item.nature == 'confirmedout'">
            <VIcon>mdi-arrow-right-bold</VIcon>{{ status(item.idbel) }}
          </span>
        </template>
        <template v-slot:item.action="{ item }">
          <VBtn density="compact" color="green" icon="mdi-pencil" variant="text"
            v-show="canEdit(item.idbel)" @click="openEditPlayer(item.idbel)" />
          <VBtn density="compact" color="red" icon="mdi-arrow-right" variant="text"
            v-show="canExport(item.idbel)" @click="openExportPlayer(item.idbel)" />
          <VBtn density="compact" color="green" icon="mdi-arrow-left" variant="text"
            v-show="canAssign(item.idbel)" @click="assignPlayer(item.idbel)" />
        </template>
      </VDataTable>
      <div>
        <VBtn @click="validatePlayerlist()" color="primary">Save</VBtn>
      </div>
    </div>
    <VDialog v-model="editdialog" width="20em">
      <VCard>
        <VCardTitle>
          Edit: {{ playeredit.fullname }}
          <VDivider />
        </VCardTitle>
        <VCardText>
          <h4>Modify assigned Elo</h4>
          <div>Current assigned rating: {{ playeredit.assignedrating }} </div>
          <div>Max ELO: {{ Math.max(playeredit.fiderating, playeredit.natrating) + 100 }}</div>
          <div>Min ELO: {{ minelo(playeredit) }}</div>
          <VTextField v-model="playeredit.natrating" label="Bel Elo" />
          <VTextField v-model="playeredit.fiderating" label="Fide Elo" />
          <VTextField v-model="playeredit.assignedrating" label="New Elo" />
          <VDivider />
          <h4>Titular</h4>
          <VSelect :items="titularchoices" v-model="playeredit.titular"></VSelect>
          <VDivider />
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
              <span v-show="err.errortype == 'TitularOrder'">
                {{ err.message }}
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
.imported {
  color: purple;
  font-weight: 500;
}

.exported,
.unassigned {
  color: rgb(186, 185, 185);
}
</style>

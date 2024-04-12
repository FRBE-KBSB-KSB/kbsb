<script setup>
import { ref } from 'vue'

// waiting
const waitingdialog = ref(false)
let dialogcounter = 0
function changeDialogCounter(i) {
  dialogcounter += i
  waitingdialog.value = (dialogcounter > 0)
}

//snackbar
const errortext = ref(null)
const snackbar = ref(null)
function displaySnackbar(text, color) {
  errortext.value = text
  snackbar.value = true
}

const { t } = useI18n()
const { $backend } = useNuxtApp()
const idclub = ref(null)
const clubs = ref([])
const icclub = ref([])
const players = ref([])
const runtimeConfig = useRuntimeConfig();


const headers = [
  { title: "N", key: "index" },
  { title: t('Name'), key: 'fullname' },
  { title: t("ID number"), key: 'idnumber', sortable: false },
  { title: "ELO", key: "assignedrating" },
  { title: "Club", key: "idcluborig" },
  { title: t("Titular"), key: "titular" },
]
const itemsPerPage = 50
const itemsPerPageOptions = [
  { value: 50, title: '50' },
  { value: 150, title: '150' },
  { value: -1, title: 'All' }
]

function download() {
  const url = `${runtimeConfig.public.apiurl}/api/v1/interclubs/anon/command/xls/playerlist?idclub=${idclub.value}`
  window.location.href = url
}

function filterPlayers() {
  if (!icclub.value.enrolled) {
    players.value = []
    return
  }
  players.value = icclub.value.players.filter((p) => p.nature != "confirmedout")
  players.value.forEach((p) => {
    p.fullname = `${p.last_name}, ${p.first_name}`
  })
}

async function getClubs() {
  let reply
  changeDialogCounter(1)
  try {
    reply = await $backend("club", "anon_get_clubs", {})
  } catch (error) {
    displaySnackbar(t(error.message))
    return
  }
  finally {
    changeDialogCounter(-1)
  }
  clubs.value = reply.data
  clubs.value.forEach(p => {
    p.merged = `${p.idclub}: ${p.name_short} ${p.name_long}`
  })
}

async function getICPlayerlist() {
  let reply
  changeDialogCounter(1)
  try {
    reply = await $backend("interclub", "anon_getICclub", {
      idclub: idclub.value
    })
  } catch (error) {
    displaySnackbar(t(error.message))
    return
  }
  finally {
    changeDialogCounter(-1)
  }
  icclub.value = reply.data
  filterPlayers()
}

function selectClub() {
  getICPlayerlist()
}

onMounted(() => {
  getClubs()
})

</script>
<template>
  <v-container>
    <h2>{{ $t('Player list') }}</h2>
    <v-card>
      <v-card-text>
        {{ $t('Select the club') }} ({{ $t('Start typing number or name') }})
        <VAutocomplete v-model="idclub" :items="clubs" item-title="merged" item-value="idclub"
          color="green" label="Club" clearable @update:model-value="selectClub">
        </VAutocomplete>
      </v-card-text>
    </v-card>
    <div v-if="idclub">
      <VBtn @click="download" class="mt-2" color="green">{{ $t('Download') }}</VBtn>
      <VDataTable :items="players" :headers="headers" density="compact"
        :items-per-page="itemsPerPage" :items-per-page-options="itemsPerPageOptions"
        :sort-by="[{ key: 'assignedrating', order: 'desc' }]">
        <template v-slot:item.index="{ item, index }">
          {{ index + 1 }}
        </template>
      </VDataTable>

    </div>
  </v-container>
</template>

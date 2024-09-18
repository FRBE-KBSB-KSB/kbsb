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

// data model
const idclub = ref(null)
const clubs = ref([])
const icclub = ref([])
const players = ref([])
const runtimeConfig = useRuntimeConfig()

const headers = [
  { title: "N", key: "index" },
  { title: t("Name"), key: "fullname" },
  { title: t("ID number"), key: "idnumber", sortable: false },
  { title: "ELO", key: "assignedrating" },
  { title: "Club", key: "idcluborig" },
  { title: t("Titular"), key: "titular" },
]
const itemsPerPage = 50
const itemsPerPageOptions = [
  { value: 50, title: "50" },
  { value: 150, title: "150" },
  { value: -1, title: "All" },
]

async function download() {
  let reply, xls
  showLoading(true)
  try {
    reply = await $backend("interclub", "anon_xls_playerlist", {
      idclub: idclub.value,
    })
    xls = reply.data.xls64
  } catch (error) {
    console.log("download error", error)
    showSnackbar("Download error: " + error.detail)
  } finally {
    showLoading(false)
  }
  const link = document.createElement("a")
  link.download = "playerlists_2425.xlsx"
  link.href = "data:application/excel;base64," + xls
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  showSnackbar("Downloading playerlists successful")
}

function filterPlayers() {
  if (!icclub.value.registered) {
    players.value = []
    return
  }
  players.value = icclub.value.players.filter((p) => p.nature != "exported")
  players.value.forEach((p) => {
    p.fullname = `${p.last_name}, ${p.first_name}`
  })
}

async function getClubs() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("club", "anon_get_clubs", {})
  } catch (error) {
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading(false)
  }
  clubs.value = reply.data
  clubs.value.forEach((p) => {
    p.merged = `${p.idclub}: ${p.name_short} ${p.name_long}`
  })
}

async function getICPlayerlist() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("interclub", "anon_getICclub", {
      idclub: idclub.value,
    })
  } catch (error) {
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading(false)
  }
  icclub.value = reply.data
  filterPlayers()
}

function selectClub() {
  getICPlayerlist()
}

async function setup() {
  console.log("setup playerlist public")
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  getClubs()
}
</script>

<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <h2>{{ $t("Player list") }}</h2>
    <v-card>
      <v-card-text>
        {{ $t("Select the club") }} ({{ $t("Start typing number or name") }})
        <VAutocomplete
          v-model="idclub"
          :items="clubs"
          item-title="merged"
          item-value="idclub"
          color="green"
          label="Club"
          clearable
          @update:model-value="selectClub"
        >
        </VAutocomplete>
      </v-card-text>
    </v-card>
    <div v-if="idclub">
      <VBtn @click="download" class="mt-2" color="green">{{ $t("Download") }}</VBtn>
      <VDataTable
        :items="players"
        :headers="headers"
        density="compact"
        :items-per-page="itemsPerPage"
        :items-per-page-options="itemsPerPageOptions"
        :sort-by="[{ key: 'assignedrating', order: 'desc' }]"
      >
        <template v-slot:item.index="{ item, index }">
          {{ index + 1 }}
        </template>
      </VDataTable>
    </div>
  </v-container>
</template>

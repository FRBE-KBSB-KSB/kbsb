<script setup>
import { ref, computed, onMounted } from 'vue'

const config = useRuntimeConfig()
const { locale } = useI18n()
const { $backend } = useNuxtApp()

const files = ref(null)
const filter = ref({ board: false, ga: false })
const headers = [
  { title: 'Report', key: 'topic' },
  { title: 'Date', key: 'topicdate' },
  { title: 'File', key: 'path' }
]
const pageoptions = [
  { value: 20, title: '20' },
  { value: 50, title: '50' },
  { value: 100, title: '100' },
  { value: -1, title: '$vuetify.dataFooter.itemsPerPageAll' }
]

const filteredfiles = computed(() => {
  if (!files.value) return []
  if (!filter.value.board && !filter.value.ga) {
    return files.value
  }
  const fa = []
  files.value.forEach((f) => {
    if (f.topic === 'Report Board Meeting' && filter.value.board) {
      fa.push(f)
    }
    if (f.topic === 'Report General Assembly' && filter.value.ga) {
      fa.push(f)
    }
  })
  return fa
})

function urlfile(url) {
  return `${config.public.apiurl}/api/v1/report/anon/filecontent/${url}`
}

async function getReports() {
  try {
    const resp = await $backend("file", "anon_get_files", { reports: 1 })
    files.value = resp.data.files
  } catch (error) {
    console.error('getting getFiles', error)
  }
}


onMounted(() => (getReports()))

</script>

<template>
  <v-container>
    <h1>{{ $t('Reports') }}</h1>
    <v-row>
      <v-col cols="6">
        <v-checkbox v-model="filter.board" :label="$t('Report Board Meeting')" />
      </v-col>
      <v-col cols="6">
        <v-checkbox v-model="filter.ga" :label="$t('Report General Assembly')" />
      </v-col>
    </v-row>
    <v-data-table :headers="headers" :items="filteredfiles" class="elevation-1" items-per-page="20"
      :items-per-page-options="pageoptions" :sort-by="[{ key: 'topicdate', order: 'desc' }]">
      <template v-slot:item.topic="{ item }">
        {{ $t(item.topic) }}
      </template>
      <template v-slot:item.path="{ item }">
        URL: <a :href="urlfile(item.raw.url)">{{ item.raw.name }}</a>
      </template>
    </v-data-table>
  </v-container>
</template>

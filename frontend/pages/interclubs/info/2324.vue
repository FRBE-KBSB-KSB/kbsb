<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import ResultsPublic from '@/components/interclubs/ResultsPublic.vue'
import Standings from '@/components/interclubs/Standings.vue'
// import VenuePublic from '@/components/interclubs/VenuePublic.vue'
// import PlayerlistPublic from '@/components/interclubs/PlayerlistPublic.vue'
// import Announcements from '@/components/interclubs/Announcements.vue'
// import Dates from '@/components/interclubs/Dates.vue'

// i18n
const { locale, t: $t } = useI18n()

const tab = ref(null)
const refresults = ref(null)
const refstandings = ref(null)
const refplayerlist = ref(null)
const refvenues = ref(null)
const refannouncements = ref(null)
const refdates = ref(null)
function changeTab() {
  console.log('changeTab', tab.value)
  switch (tab.value) {
    case 'results':
      refresults.value.setup()
      break
    case 'standings':
      refstandings.value.setup()
      break
  }
}

onMounted(() => {
  tab.value = "results"
  changeTab()
})

</script>

<template>
  <v-container>
    <h1>Interclubs 2023-24</h1>
    <v-tabs v-model="tab" color="green" @update:modelValue="changeTab">
      <v-tab value="results">{{ $t('Results') }}</v-tab>
      <v-tab value="standings">{{ $t('Standings') }}</v-tab>
    </v-tabs>
    <v-window v-model="tab" @update:modelValue="changeTab">
      <v-window-item :eager="true" value="results">
        <ResultsPublic ref="refresults" />
      </v-window-item>
      <v-window-item :eager="true" value="standings">
        <Standings ref="refstandings" />
      </v-window-item>
    </v-window>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
// import ResultsPublic from '@/components/interclubs/ResultsPublic.vue'
// import Standings from '@/components/interclubs/Standings.vue'
// import VenuePublic from '@/components/interclubs/VenuePublic.vue'
// import PlayerlistPublic from '@/components/interclubs/PlayerlistPublic.vue'
// import Announcements from '@/components/interclubs/Announcements.vue'
// import Dates from '@/components/interclubs/Dates.vue'

// i18n
const { locale, t: t } = useI18n()

// const tab = ref(null)
// const refresults = ref(null)
// const refstandings = ref(null)
// const refplayerlist = ref(null)
// const refvenues = ref(null)
// const refannouncements = ref(null)
// const refdates = ref(null)
// function changeTab() {
//   console.log('changeTab', tab.value)
//   switch (tab.value) {
//     case 'results':
//       refresults.value.setup()
//       break
//     case 'standings':
//       refstandings.value.setup()
//       break
//     case 'playerlist':
//       refplayerlist.value.setup()
//       break
//     case 'venues':
//       refvenues.value.setup()
//       break    
//     case 'announcements':
//       refannouncements.value.setup()
//       break
//     case 'dates':
//       refdates.value.setup()
//       break
//   }
// }

// onMounted(() => {
//   tab.value = "results"
//   changeTab()
// })

</script>

<template>
  <v-container>
    <h1>Interclubs 2024-25</h1>
    <div>
      <div v-if="locale == 'nl'">
        Het nieuwe seizoen start in september 2024.
      </div>
      <div v-if="locale == 'fr'">
        La nouvelle saison commence en septembre 2024.
      </div>
      <div v-if="locale == 'en'">
        The new season starts in September 2024.
      </div>
      <div v-if="locale == 'de'">
        Die neue Saison beginnt im September 2024.
      </div>      
      
    </div>
    <!-- <v-tabs v-model="tab" color="green" @update:modelValue="changeTab"> -->
      <!-- <v-tab value="results">{{ t('Results') }}</v-tab>
      <v-tab value="standings">{{ t('Standings') }}</v-tab> -->
      <!-- <v-tab value="playerlist">{{ t('Player list') }}</v-tab>
      <v-tab value="venues">{{ t('Venues') }}</v-tab>
      <v-tab value="announcements">{{ t('Announcements') }}</v-tab>
      <v-tab value="dates">{{ t('Dates') }}</v-tab> -->
    <!-- </v-tabs>
    <v-window v-model="tab" @update:modelValue="changeTab">
      <v-window-item :eager="true" value="results">
        <ResultsPublic ref="refresults" />
      </v-window-item>
      <v-window-item :eager="true" value="standings">
        <Standings ref="refstandings" />
      </v-window-item> -->
      <!-- <v-window-item :eager="true" value="playerlist">
        <PlayerlistPublic ref="refplayerlist"/>
      </v-window-item>      
      <v-window-item :eager="true" value="venues">
        <VenuePublic ref="refvenues"/>
      </v-window-item>
      <v-window-item :eager="true" value="announcements">
        <Announcements ref="refannouncements"/>
      </v-window-item>
      <v-window-item :eager="true" value="dates">
        <Dates ref="refdates"/>
      </v-window-item> -->
    <!-- </v-window> -->
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { VContainer, VCard, VCardTitle, VCardText, VDivider, VCol, VRow, VBtn,
  VDialog, VProgressCircular, VAutocomplete} from 'vuetify/lib/components/index.mjs';

// communication with manager
const emit = defineEmits(['displaySnackbar',  'changeDialogCounter'])
defineExpose({ setup })

// waiting
const waitingdialog = ref(false)
let dialogcounter = 0
function changeDialogCounter(i) {
    dialogcounter += i
    waitingdialog.value = (dialogcounter > 0)
}

// snackbar
const errortext = ref(null)
const snackbar = ref(null)
function displaySnackbar(text, color) {
  errortext.value = text
  snackbar.value = true
}

// datamodel
const { t: $t } = useI18n()
const { $backend } = useNuxtApp()
const icstandings = ref([])
const icclubs = ref([])
const idclub = ref(null)

async function getClubs() {
  let reply
  emit('changeDialogCounter', 1)
  try {
    reply = await $backend("interclub","anon_getICclubs", {})
  } catch (error) {
    emit('displaySnackbar', $t(error.message))
    return
  }
  finally {
    emit('changeDialogCounter', -1)
  }
  icclubs.value = reply.data
  icclubs.value.forEach((p) => {
    p.merged = `${p.idclub}: ${p.name}`
  }) 
}

async function getStandings() {
  let reply
  emit('changeDialogCounter', 1)
  try {
    reply = await $backend("interclub","anon_getICstandings", {
      idclub: idclub.value
    })
  } catch (error) {
    emit('displaySnackbar', $t(error.message))
    return
  }
  finally {
    emit('changeDialogCounter', -1)
  }
  icstandings.value = reply.data
}

function setup(){
  console.log('setup standings')
  getClubs()
}

</script>

<template>
  <v-container>
    <h2>{{ $t('Standings') }}</h2>
    <v-row>
      <v-col cols="8">
        <VAutocomplete v-model="idclub" :items="icclubs" 
          item-title="merged" item-value="idclub" color="green"
          label="Club" clearable  >
        </VAutocomplete>        
      </v-col>
      <v-col cols="4">
        <VBtn icon="mdi-play" @click="getStandings"></VBtn>
      </v-col>
    </v-row>
    <v-card v-for="s in icstandings" class="my-2">
      <v-card-title> 
        {{ $t('Division') }} {{ s.division }}{{ s.index }}
        <VDivider />
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col>#</v-col>
          <v-col cols="6">{{ $t('Team') }}</v-col>
          <v-col># {{ $t('Played') }}</v-col>
          <v-col><b>MP</b></v-col>
          <v-col>BP</v-col>
        </v-row>
        <v-row v-for="(t, ix) in s.teams">
          <v-col>{{ ix + 1 }}</v-col>
          <v-col cols="6">{{ t.name }} ({{ t.idclub }})</v-col>
          <v-col>{{ t.games.length }}</v-col>
          <v-col><b>{{ t.matchpoints }}</b></v-col>
          <v-col>{{ t.boardpoints }}</v-col>
        </v-row>
      </v-card-text>
    </v-card>
    <v-dialog width="10em" v-model="waitingdialog">
      <v-card>
        <v-card-title>{{ $t('Loading...')}}</v-card-title>
        <v-card-text>
          <v-progress-circular indeterminate color="green" />
        </v-card-text>
      </v-card>
    </v-dialog> 
  </v-container>
</template>

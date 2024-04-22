<script setup>
import {ref, computed, nextTick} from 'vue'
import { VContainer, VAutocomplete, VSelect, VBtn, VCard, VCardTitle, VCardText, VRow, 
  VCol, VDivider, VCheckbox, VDialog, VProgressCircular} from 'vuetify/lib/components/index.mjs';

const { t } = useI18n()
const { $backend } = useNuxtApp()

const idclub = ref(null)
const clubs = ref([])
const icvenues = ref([])
const waitingdialog = ref(false)
let dialogcounter = 0

function changeDialogCounter(i) {
    dialogcounter += i
    waitingdialog.value = (dialogcounter > 0)
}

function displaySnackbar(text, color) {
  errortext.value = text
  snackbar.value = true
}

async function getClubs() {
  let reply
  changeDialogCounter(1)
  try {
    reply = await $backend("club","anon_get_clubs", {})
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

async function getICVenues() {
  let reply
  changeDialogCounter(1)
  try {
    reply = await $backend("interclub","anon_getICVenues", {
        idclub: idclub.value
    })
  } catch (error) {    
    displaySnackbar(t(error.message))
    return
  }
  finally {
    changeDialogCounter(-1)
  }
  icvenues.value = reply.data.venues   
}

function selectClub(){
  getICVenues()
}

onMounted( () => {
  getClubs()
})

</script>
<template>
  <v-container>
    <h2>{{ $t('Interclub venues') }}</h2>
    <v-card>
      <v-card-text>
        {{ $t('Select the club') }} ({{ $t('Start typing number or name') }})
        <VAutocomplete v-model="idclub" :items="clubs" 
          item-title="merged" item-value="idclub" color="green"
          label="Club" clearable @update:model-value="getICVenues" >
        </VAutocomplete>
      </v-card-text>
    </v-card>
    <div v-if="idclub">
      <v-row v-show="!icvenues.length">
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{  $t('Venues') }}
            </v-card-title>
            <v-card-text>
              {{ $t('No interclub venue is defined yet') }}
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" sm="6" md="4" xl="3" v-for="(v, ix) in icvenues" :key="ix" >
          <v-card class="elevation-5">
            <v-card-title>
              {{ $t('Venue') }}: {{ ix + 1 }}
            </v-card-title>
            <v-card-text>
              <div><b>{{ $t('Address') }}:</b> <br />
                <span v-html="v.address.split('\n').join('<br />')"></span>
              </div>
              <div><b>{{ $t('Capacity (boards)') }}:</b> {{ v.capacity }}</div>
              <div><b>{{ $t('Not available') }}:</b> {{ v.notavailable.join(', ') }}</div>
              <div><b>{{ $t('Email address venue') }}:</b> {{ v.email }}</div>
              <div><b>{{ $t('Telephone number venue') }}:</b> {{ v.phone }}</div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
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

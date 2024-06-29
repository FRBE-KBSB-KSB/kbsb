<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { INTERCLUBS_STATUS, INTERCLUBS_ROUNDS, EMPTY_VENUE } from '@/util/interclubs.js'
import { useIdtokenStore } from '@/store/idtoken'
import { storeToRefs } from 'pinia'

// communication 
const router = useRouter()
const emit = defineEmits(['displaySnackbar', 'changeDialogCounter'])
defineExpose({ setup })


// idtoken
const idstore = useIdtokenStore()
const { token: idtoken } = storeToRefs(idstore)
const { $backend } = useNuxtApp()

// datamodel
const idclub = ref(0)
const rounds = Object.entries(INTERCLUBS_ROUNDS).map(x => ({
  value: x[1], title: `R${x[0]}: ${x[1]}`
}))
const statuscm = ref(INTERCLUBS_STATUS.CONSULTING)
const status_consulting = computed(() => (statuscm.value == INTERCLUBS_STATUS.CONSULTING))
const status_modifying = computed(() => (statuscm.value == INTERCLUBS_STATUS.MODIFYING))
const venues = ref([])
const accessdenied = ref(true)
const venuestatus = ref("closed")

// i18n
const { locale, t } = useI18n()


function addEmptyVenue() {
  const last = venues.value[venues.value.length - 1]
  if (!last || last.address !== '') {
    venues.value.push({ ...EMPTY_VENUE })
  }
}

function cancelVenues() {
  statuscm.value = INTERCLUBS_STATUS.CONSULTING
}

function deleteVenue(ix) {
  venues.value, splice(ix, 1)
  addEmptyVenue()
}

async function getICVenues() {
  if (!idclub.value) {
    venues.value = []
    accessdenied.value = true
    return
  }
  let reply
  emit('changeDialogCounter', 1)
  try {
    reply = await $backend("club", "verify_club_access", {
      idclub: idclub.value,
      role: "InterclubAdmin",
      token: idtoken.value,
    })
    accessdenied.value = false
  } catch (error) {
    if (error.code == 401) {
      gotoLogin()
    }
    if (error.code == 403) {
      accessdenied.value = true
    }
    return
  } finally {
    emit('changeDialogCounter', -1)
  }
  emit('changeDialogCounter', 1)
  try {
    reply = await $backend("interclub", "anon_getICVenues", {
      idclub: idclub.value
    })
  } catch (error) {
    displaySnackbar(t(error.message))
    return
  }
  finally {
    emit('changeDialogCounter', -1)
  }
  venues.value = reply.data.venues
  venues.value.forEach((v) => {
    v.available = v.notavailable.length ? "selected" : "all"
  })
}

async function gotoLogin() {
  await router.push('/tools/oldlogin?url=__interclubs__manager')
}

function modifyICvenues() {
  statuscm.value = INTERCLUBS_STATUS.MODIFYING
  addEmptyVenue()
}

async function saveVenues() {
  let reply
  try {
    let savedvenues = []
    venues.value.forEach(v => {
      if (v.address && v.address.length) {
        let { available, ...others } = v
        savedvenues.push(others)
      }
    })
    reply = await $backend("interclub", "set_interclubvenues", {
      token: idtoken.value,
      idclub: idclub.value,
      venues: savedvenues,
    })
  } catch (error) {
    if (error.code == 401) gotoLogin()
    emit('displaySnackbar', t(error.message))
    return
  }
  statuscm.value = INTERCLUBS_STATUS.CONSULTING
  emit('displaySnackbar', t('Interclub venue saved'))
}

function setup(clb) {
  console.log('setup venues', clb)
  venuestatus.value = 'closed'
  // idclub.value = clb.idclub
  // getICVenues()
}

</script>
<template>
  <v-container>
    <v-alert type="warning" variant="outlined" v-if="venuestatus == 'closed'"
      :text="t('Currently the venues cannot be modified')" />
    <v-alert type="warning" variant="outlined" v-if="venuestatus == 'noclub'"
      :text="t('Please select a club')" />
    <v-alert type="warning" variant="outlined" v-if="venuestatus == 'noaccess'"
      :text="t('Permission denied')" />
    <div v-if="venuestatus == 'open'">
      <v-container v-show="status_consulting">
        <v-row v-show="!venues.length">
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card class="elevation-5">
              <v-card-title class="card-title">
                {{ $t('Venues') }}
              </v-card-title>
              <v-card-text>
                {{ $t('No interclub venue is defined yet') }}
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3" v-for="(v, ix) in venues" :key="ix">
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
                <p>{{ $t('Optional') }}</p>
                <div><b>{{ $t('Email address venue') }}:</b> {{ v.email }}</div>
                <div><b>{{ $t('Telephone number venue') }}:</b> {{ v.phone }}</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row>
          <v-btn @click="modifyICvenues">
            {{ $t('Edit') }}
          </v-btn>
        </v-row>
      </v-container>
      <v-container v-show="status_modifying">
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3" v-for="(v, ix) in venues" :key="ix">
            <v-card class="elevation-5">
              <v-card-title>
                {{ $t('Venue') }}: {{ ix + 1 }}
              </v-card-title>
              <v-card-text>
                <v-textarea v-model="v.address" :label="$t('Address')" rows="3"
                  @input="addEmptyVenue" outlined />
                <v-text-field v-model="v.capacity" :label="$t('Capacity (boards)')" type="number" />
                <h4>{{ $t('Availability') }}</h4>
                <v-radio-group v-model="v.available">
                  <v-radio value="all" :label="$t('All rounds')" />
                  <v-radio value="selected"
                    :label="$t('The venue is not available on following rounds')" />
                </v-radio-group>
                <v-select multiple v-show="v.available != 'all'" :items="rounds" chips
                  v-model="v.notavailable"
                  :label="$t('Select the rounds the venue is not available')" />
                <p class="fieldname">{{ $t('Optionally') }}</p>
                <v-text-field v-model="v.email" :label="$t('Email address venue')" />
                <v-text-field v-model="v.phone" :label="$t('Telephone number venue')" />
                <v-textarea v-model="v.remarks" :label="$t('Remarks')" />
              </v-card-text>
              <v-card-actions>
                <v-btn fab small @click="deleteVenue(ix)" v-show="ix < venues.length - 1">
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
        <v-row>
          <v-btn @click="saveVenues">
            {{ $t('Save Venues') }}
          </v-btn>
          <v-btn @click="cancelVenues">
            {{ $t('Cancel') }}
          </v-btn>
        </v-row>
      </v-container>
    </div>

  </v-container>
</template>

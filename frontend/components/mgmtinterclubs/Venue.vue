<script setup>
import { ref, computed } from 'vue'
import { INTERCLUBS_STATUS, INTERCLUBS_ROUNDS, EMPTY_VENUE } from '@/util/interclubs'

// stores
import { useMgmtTokenStore } from "@/store/mgmttoken"
import { useMgmtInterclubStore } from "@/store/mgmtinterclub"
import { storeToRefs } from 'pinia'
const mgmttokenstore = useMgmtTokenStore()
const { token: mgmttoken } = storeToRefs(mgmttokenstore)
const mgmtinterclubstore = useMgmtInterclubStore()
const { club } = storeToRefs(mgmtinterclubstore)

// communication with manager
defineExpose({ checkStore })
const { $backend } = useNuxtApp()

//  snackbar and loading widgets
import ProgressLoading from '@/components/ProgressLoading.vue'
import SnackbarMessage from '@/components/SnackbarMessage.vue'
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

// datamodel
const my = ref({
  idclub: 0,
  round: 0
})
const showVenues = computed(() => my.value.idclub)
const roundchoices = Object.entries(INTERCLUBS_ROUNDS).map(x => ({
  value: x[1], title: `R${x[0]}: ${x[1]}`
}))
const statuscm = ref(INTERCLUBS_STATUS.CONSULTING)
const status_consulting = computed(() => (statuscm.value == INTERCLUBS_STATUS.CONSULTING))
const status_modifying = computed(() => (statuscm.value == INTERCLUBS_STATUS.MODIFYING))
const venues = ref([])


// methods 
function addEmptyVenue() {
  const last = venues.value[venues.value.length - 1]
  if (!last || last.address !== '') {
    venues.value.push({ ...EMPTY_VENUE })
  }
}

function cancelVenues() {
  statuscm.value = INTERCLUBS_STATUS.CONSULTING
}


function checkStore() {
  console.log('checkStore venues', club.value.idclub)
  my.value.idclub = club.value.idclub
  getICVenues()
}

function deleteVenue(ix) {
  venues.value.splice(ix, 1)
  addEmptyVenue()
}

async function getICVenues() {
  let reply
  if (!my.value.idclub) {
    venues.value = []
    return
  }
  showLoading(true)
  try {
    reply = await $backend("interclub", "anon_getICVenues", {
      idclub: my.value.idclub
    })
  } catch (error) {
    console.log('NOK getICVenues')
    showSnackbar(error.message)
    return
  }
  finally {
    showLoading(false)
  }
  venues.value = reply.data.venues
  venues.value.forEach((v) => {
    v.available = v.notavailable.length ? "selected" : "all"
    venues.value.push(v)
  })
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
    showLoading(true)
    reply = await $backend("interclub", "mgmt_set_interclubvenues", {
      token: mgmttoken.value,
      idclub: my.idclub,
      venues: savedvenues,
    })
  } catch (error) {
    showSnackbar(error.message)
    return
  }
  finally {
    showLoading(false)
  }
  statuscm.value = INTERCLUBS_STATUS.CONSULTING
  showSnackbar('Interclub venue saved')
}


onMounted(() => {
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
})

</script>
<template>
  <VContainer>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <h2>Interclub venues</h2>
    <p v-show="!showVenues">Please select a club to view the interclubs player list</p>
    <div v-show="showVenues">
      <v-container v-show="status_consulting">
        <v-row v-show="!venues.length">
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card class="elevation-5">
              <v-card-title class="card-title">
                Venues
              </v-card-title>
              <v-card-text>
                No interclub venue is defined
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3" v-for="(v, ix) in venues" :key="ix">
            <v-card class="elevation-5">
              <v-card-title>
                Venue: {{ ix + 1 }}
              </v-card-title>
              <v-card-text>
                <div><b>Address:</b> <br />
                  <span v-html="v.address.split('\n').join('<br />')"></span>
                </div>
                <div><b>Capacity (boards):</b> {{ v.capacity }}</div>
                <div><b>Not available:</b> {{ v.notavailable.join(', ') }}</div>
                <p>Optional</p>
                <div><b>Email address venue:</b> {{ v.email }}</div>
                <div><b>Telephone number venue:</b> {{ v.phone }}</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row>
          <v-btn @click="modifyICvenues">
            Edit
          </v-btn>
        </v-row>
      </v-container>
      <v-container v-show="status_modifying">
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3" v-for="(v, ix) in venues" :key="ix">
            <v-card class="elevation-5">
              <v-card-title>
                Venue: {{ ix + 1 }}
              </v-card-title>
              <v-card-text>
                <v-textarea v-model="v.address" label="Address" rows="3" @input="addEmptyVenue"
                  outlined />
                <v-text-field v-model="v.capacity" label="Capacity (boards)" type="number" />
                <h4>Availability</h4>
                <v-radio-group v-model="v.available">
                  <v-radio value="all" label="All rounds" />
                  <v-radio value="selected" label="The venue is not available on following rounds" />
                </v-radio-group>
                <v-select multiple v-show="v.available != 'all'" :items="roundchoices" chips
                  v-model="v.notavailable" label="Select the rounds the venue is not available" />
                <p class="fieldname">Optionally</p>
                <v-text-field v-model="v.email" label="Email address venue" />
                <v-text-field v-model="v.phone" label="Telephone number venue" />
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
            Save Venues
          </v-btn>
          <v-btn @click="cancelVenues">
            Cancel
          </v-btn>
        </v-row>
      </v-container>
    </div>
  </VContainer>
</template>

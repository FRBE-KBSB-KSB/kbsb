<script setup>
import { ref, computed } from 'vue'
import { VContainer, VBtn, VCard, VCardTitle, VCardText, VRow, VCol, 
  VAutocomplete, VSelect, VTextField,  } from 'vuetify/components'
import { visibility_items, CLUB_STATUS, EMPTY_BOARD, EMPTY_CLUB } from '@/util/club'

// stores
import { useMgmtTokenStore } from "@/store/mgmttoken"
import { storeToRefs } from 'pinia'
const mgmtstore = useMgmtTokenStore()
const { token: mgmttoken } = storeToRefs(mgmtstore) 

//  snackbar and loading widgets
import ProgressLoading from '@/components/ProgressLoading.vue'
import SnackbarMessage from '@/components/SnackbarMessage.vue'
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

// datamodel
const boardmembers = ref(EMPTY_BOARD)
const clubdetails = ref(EMPTY_CLUB)
const clubmembers = ref([])
const statuscm = ref(CLUB_STATUS.CONSULTING)
const status_consulting = computed(() => (statuscm.value == CLUB_STATUS.CONSULTING))
const status_modifying = computed(() => (statuscm.value == CLUB_STATUS.MODIFYING))
const t_vis_items = computed(()=>  visibility_items.map((x) =>({
  title: x.title,
  value: x.value
})))
let copyclubdetails = null

// communication
const emit = defineEmits(['updateClub'])
const { $backend } = useNuxtApp()


function cancelClub() {
  statuscm.value = CLUB_STATUS.CONSULTING
  emit('updateClub')
}

function copyClubMembers(cm) {
  clubmembers.value = cm
}


function gotoLogin() {
  navigateTo('/mgmt')
}

async function modifyClub() {
  statuscm.value = CLUB_STATUS.MODIFYING
}

function readClubDetails(club) {
  console.log('readClubDetails in board')  
  clubdetails.value = { ...EMPTY_CLUB, ...club }
  copyclubdetails = JSON.parse(JSON.stringify(club))
  boardmembers.value = { ...EMPTY_BOARD, ...club.boardmembers }
}

async function saveClub() {
  // build a a diff between clubdetails and its cooy
  showLoading(true)
  let update = {}
  for (const [key, value] of Object.entries(clubdetails.value)) {
    if (value != copyclubdetails[key]) {
      update[key] = value
    }
  }
  try {
    const reply = await $backend("club", "mgmt_update_club",{
      ...update,
      idclub: clubdetails.value.idclub,
      token: mgmttoken.value,
    })
    statuscm.value = CLUB_STATUS.CONSULTING
    showSnackbar('Club saved')
    emit('updateClub')
  } catch (error) { 
    if (error.code == 401) gotoLogin()
    showSnackbar(error.message)
    return
  }
  finally {
    showLoading(false)
  }
}

function updateboard(f) {
  const bm = boardmembers.value[f]
  if (bm.idnumber) {
    let cm = clubmembers.value.find(x => x.idnumber == bm.idnumber)
    bm.first_name = cm.first_name
    bm.last_name = cm.last_name
    bm.email = cm.email
    bm.mobile = cm.mobile
    bm.email_visibility = "CLUB"
    bm.mobile_visibility = "CLUB"
    clubdetails.value.boardmembers[f] = bm
  }
  else {
    bm.first_name = null
    bm.last_name = null
    bm.email = null
    bm.mobile = null
    bm.email_visibility = null
    bm.mobile_visibility = null
    delete clubdetails.value.boardmembers[f]
 }
}

function setup(club){
  console.log('setupBoard', club)
  readClubDetails(club)
}

defineExpose({setup, copyClubMembers})

onMounted( () => {
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
})


</script>


<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading"/>    
    <p v-if="!clubdetails.idclub">Select a club to view the club details</p>
    <div v-if="clubdetails.idclub">
      <v-container v-if="status_consulting">
        <h2>Consulting board members</h2>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3" v-for="(bm, f) in boardmembers" :key="f">
            <v-card class="elevation-5">
              <v-card-title>
                {{ f }}
              </v-card-title>
              <v-card-text>
                Name: {{ bm.first_name }} {{ bm.last_name }}<br />
                Email: {{ bm.email }}<br />
                Mobile: {{ bm.mobile }}
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row class="mt-2">
          <v-btn @click="modifyClub">Modify</v-btn>
        </v-row>        
      </v-container>
      <v-container v-if="status_modifying">
        <h2>Modify board members</h2>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3" v-for="(bm, f) in boardmembers" :key="f">
            <v-card class="elevation-5">
              <v-card-title>
                {{  f  }}
              </v-card-title>
              <v-card-text>
                <v-autocomplete v-model="boardmembers[f].idnumber" :items="clubmembers" item-title="merged"
                  item-value="idnumber" color="green" clearable  @update:model-value="updateboard(f)">
                </v-autocomplete>
                <v-text-field label="Email" v-model="boardmembers[f].email"></v-text-field>
                <v-select v-model="boardmembers[f].email_visibility" :items="t_vis_items" color="green"
                  label="Email visibility" />
                <v-text-field label="GSM" v-model="boardmembers[f].mobile"></v-text-field>
                <v-select v-model="boardmembers[f].mobile_visibility" :items="t_vis_items" color="green"
                  label="Mobile visibility" />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>     
        <v-row class="ma-2">
          <v-btn @click="saveClub">Save club</v-btn>
          <v-btn @click="cancelClub">Cancel</v-btn>
        </v-row>
      </v-container>
    </div>
  </v-container>
</template>

<style scoped>
.fieldname {
  color: green;
}
.v-card__text, .v-card__title {
  word-break: normal; /* maybe !important  */
}
</style>

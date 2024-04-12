<script setup>
import {ref, computed, nextTick} from 'vue'
import { VContainer, VBtn, VCard, VCardTitle, VCardText,  VRow, VCol, 
  VAutocomplete, VIcon, VTextField, VTextarea, } from 'vuetify/components';
import { visibility_items, CLUB_STATUS, EMPTY_CLUB } from '@/util/club'

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
const clubdetails = ref(EMPTY_CLUB)
const clubadmin = ref ({})
const clubmembers = ref([])
let copyclubdetails = null
const interclubadmin = ref ({})
const interclubcaptain = ref({})
const newclubadmin = ref (null)
const newinterclubadmin = ref (null)
const newinterclubcaptain= ref( null)
const statuscm = ref(CLUB_STATUS.CONSULTING)
const status_consulting = computed(() => (statuscm.value == CLUB_STATUS.CONSULTING))
const status_modifying = computed(() => (statuscm.value == CLUB_STATUS.MODIFYING))
const t_vis_items = computed(()=>  visibility_items.map((x) =>({
  title: x.title,
  value: x.value
})))
let clubadminl, interclubadminl, interclubcaptainl;

// communication
const emit = defineEmits(['updateClub'])
const { $backend } = useNuxtApp()

function addClubAdmin() {
  const cm = clubmembers.value.find(m => m.idnumber == newclubadmin.value)
  clubadmin.value[newclubadmin.value] = cm.merged
  nextTick(() => newclubadmin.value = null);
}

function addInterclubAdmin() {
  interclubadmin.value[newinterclubadmin.value] = clubmembers.value.find(
    m => m.idnumber == newinterclubadmin.value).merged
  nextTick(() => newinterclubadmin.value = 0);
}

function addInterclubCaptain() {
  interclubcaptain.value[newinterclubcaptain.value] = clubmembers.value.find(
    m => m.idnumber == newinterclubcaptain.value).merged
  nextTick(() => newinterclubcaptain.value = 0);
}

function cancelAccess() {
  statuscm.value = CLUB_STATUS.CONSULTING
  emit('updateClub')
}

function copyClubMembers(cms){
  clubmembers.value = cms
  if (clubadminl) {
    clubadmin.value = Object.fromEntries(clubadminl.map(
      (x) => {
        const cm = clubmembers.value.find(m => m.idnumber == x)
        cm.merged = cm ? `${x} ${cm.first_name} ${cm.last_name}` : ""
        return [x, cm.merged]
      }
    ))
  }
  if (interclubadminl) {
    interclubadmin.value = Object.fromEntries(interclubadminl.map(
      (x) => {
        const cm = clubmembers.value.find(m => m.idnumber == x)
        cm.merged = cm ? `${x} ${cm.first_name} ${cm.last_name}` : ""
        return [x, cm.merged]
      }
    )) 
  }
  if (interclubcaptainl) {
    interclubcaptain.value = Object.fromEntries(interclubcaptainl.map(
      (x) => {
        const cm = clubmembers.value.find(m => m.idnumber == x)
        cm.merged = cm ?`${x} ${cm.first_name} ${cm.last_name}` : ""
        return [x, cm.merged]
      }
    ))
  }
}

function deleteClubAdmin(m) {
  // don't delete last member
  if (Object.keys(clubadmin.value).length == 1) return
  delete clubadmin.value[m]
}

function deleteInterclubAdmin(m) {
  // don't delete last member
  if (Object.keys(interclubadmin).length == 1) return
  delete interclubadmin.value[m]
}

function deleteInterclubCaptain(m) {
  delete interclubcaptains.value[m]
}

function gotoLogin() {
  navigateTo(localePath('/tools/oldlogin?url=__club__manager'))
}

async function modifyAccess() {
  statuscm.value = CLUB_STATUS.MODIFYING
}

function readClubDetails(club) {
  console.log('readClubDetails in access')
  clubdetails.value = { ...EMPTY_CLUB, ...club }
  copyclubdetails = JSON.parse(JSON.stringify(club))  
  clubdetails.value.clubroles.forEach((c) => {
    if (c.nature == "ClubAdmin") clubadminl = c.memberlist
    if (c.nature == "InterclubAdmin") interclubadminl = c.memberlist
    if (c.nature == "InterclubCaptain") interclubcaptainl = c.memberlist
  })  
}

async function saveAccess() {
  // build a a diff between clubdetails and its cooy
  clubdetails.value.clubroles.forEach((c) =>{
    if (c.nature == "ClubAdmin") c.memberlist = Object.keys(clubadmin.value)
    if (c.nature == "InterclubAdmin") c.memberlist = Object.keys(interclubadmin.value)
    if (c.nature == "InterclubCaptain") c.memberlist = Object.keys(clubadmin.value)
  })
  try {
    showLoading(true)
    const reply = await $backend("club", "mgmt_update_club",{
      clubroles: clubdetails.value.clubroles,
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
  } finally {
    showLoading(false)
  }
}

function setup(club){
  console.log('setupAccess', club)
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
    <p v-if="!clubdetails.idclub">Select a club to view the access rights</p>
    <div v-if="clubdetails.idclub" class="markdowncontent">
      <v-container v-show="status_consulting">
        <h2>Consulting access rights</h2>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>Club administrators</v-card-title>
              <v-card-text>
                The club administrators have write access to the Club Manager
                <ul>
                  <li v-for="(m, ix) in clubadmin" :key="ix">{{ m }}</li>
                </ul>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>Interclub Administrators</v-card-title>
              <v-card-text>
                The interclub administrators have write access to the Interclub Manager
                <ul>
                  <li v-for="(m, ix) in interclubadmin" :key="ix">{{ m }}</li>
                </ul>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>
                Interclub Captains
              </v-card-title>
              <v-card-text>
                The interclub captains have write access to the planning and results of the Interclub.
                <p>Not available yet</p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row class="ma-2">
          <v-btn @click="modifyAccess">Modify</v-btn>
        </v-row>
      </v-container>
    
      <v-container  v-show="status_modifying">
        <h2>{Modify access rights</h2>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>Club administrators</v-card-title>
              <v-card-text>
                <ul>
                  <li v-for="(m, ix) in clubadmin" :key="m">
                    {{ m }} &nbsp; <v-icon @click="deleteClubAdmin(ix)">mdi-delete</v-icon>
                  </li>
                </ul>
                <v-autocomplete v-model="newclubadmin" :items="clubmembers || []" @update:model-value="addClubAdmin"
                  label="Add Member" class="memberselect" item-title="merged" item-value="idnumber">
                </v-autocomplete>              
              </v-card-text>
            </v-card>
          </v-col>        
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>Interclub Administrators</v-card-title>
              <v-card-text>
                <ul>
                  <li v-for="(m, ix) in interclubadmin" :key="m">
                    {{ m }} &nbsp; <v-icon @click="deleteInterclubAdmin(ix)">mdi-delete</v-icon>
                  </li>
                </ul>
                <v-autocomplete v-model="newinterclubadmin" :items="clubmembers || []"
                  @update:model-value="addInterclubAdmin" label="Add Member" class="memberselect"  item-title="merged" item-value="idnumber">
                </v-autocomplete>              
              </v-card-text>
            </v-card>
          </v-col>        
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>Club administrators</v-card-title>
              <v-card-text>Not available yet</v-card-text>
            </v-card>
          </v-col>        
        </v-row>
        <v-row class="ma-2">
          <v-btn @click="saveAccess">Save</v-btn>
          <v-btn @click="cancelAccess">Cancel</v-btn>
        </v-row>
      </v-container>
    </div>

  </v-container>
</template>

<style scoped>
.memberselect {
  max-width: 20em;
}
</style>
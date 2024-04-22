<script setup>
import {ref, computed, nextTick} from 'vue'
import { VContainer, VBtn, VCard, VCardTitle, VCardText, VAutocomplete,VIcon, 
  VRow, VCol } from 'vuetify/lib/components/index.mjs';
import { visibility_items, CLUB_STATUS, EMPTY_CLUB } from '@/util/club'
import { useIdtokenStore}  from '@/store/idtoken'
import { storeToRefs } from 'pinia'

const { localePath } = useLocalePath()
const { locale, t } = useI18n()
const { $backend } = useNuxtApp()
const props = defineProps(["club","clubmembers"])
const idstore = useIdtokenStore()
const { token: idtoken } = storeToRefs(idstore)
const clubdetails = ref(EMPTY_CLUB)
const clubadmin = ref ({})
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
  title: t(x.title),
  value: x.value
})))
let clubadminl, interclubadminl, interclubcaptainl;
const emit = defineEmits(['displaySnackbar', 'updateClub'])

function addClubAdmin() {
  const cm = props.clubmembers.find(m => m.idnumber == newclubadmin.value)
  clubadmin.value[newclubadmin.value] = cm.merged
  nextTick(() => newclubadmin.value = null);
}

function addInterclubAdmin() {
  interclubadmin.value[newinterclubadmin.value] = props.clubmembers.find(
    m => m.idnumber == newinterclubadmin.value).merged
  nextTick(() => newinterclubadmin.value = 0);
}

function addInterclubCaptain() {
  interclubcaptain.value[newinterclubcaptain.value] = props.clubmembers.find(
    m => m.idnumber == newinterclubcaptain.value).merged
  nextTick(() => newinterclubcaptain.value = 0);
}

function cancelAccess() {
  statuscm.value = CLUB_STATUS.CONSULTING
  emit('updateClub')
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

function readClubDetails() {
  console.log('reading club rights') 
  clubdetails.value = { ...EMPTY_CLUB, ...props.club }
  copyclubdetails = JSON.parse(JSON.stringify(props.club))  
  clubdetails.value.clubroles.forEach((c) => {
    console.log('loop c', c.nature, c.memberlist)
    if (c.nature == "ClubAdmin") clubadminl = c.memberlist
    if (c.nature == "InterclubAdmin") interclubadminl = c.memberlist
    if (c.nature == "InterclubCaptain") interclubcaptainl = c.memberlist
  })  
  console.log('clubadmin', clubadmin.value)  
}

function readClubMembers(){
  console.log('reading club members', clubadminl )
  clubadmin.value = Object.fromEntries(clubadminl.map(
    (x) => {
      const cm = props.clubmembers.find(m => m.idnumber == x)
      if (!cm) {
        console.log('Did not find', x)
        return []
      }
      else {
        cm.merged = cm ? `${x} ${cm.first_name} ${cm.last_name}` : ""
        return [x, cm.merged]      
      }
    }
  ))
  interclubadmin.value = Object.fromEntries(interclubadminl.map(
    (x) => {
      const cm = props.clubmembers.find(m => m.idnumber == x)
      if (!cm) {
        console.log('Did not find', x)
        return []
      }
      else {
        cm.merged = cm ? `${x} ${cm.first_name} ${cm.last_name}` : ""
        return [x, cm.merged]      
      }      
    }
  )) 
  interclubcaptain.value = Object.fromEntries(interclubcaptainl.map(
    (x) => {
      const cm = props.clubmembers.find(m => m.idnumber == x)
      if (!cm) {
        console.log('Did not find', x)
        return []
      }
      else {
        cm.merged = cm ? `${x} ${cm.first_name} ${cm.last_name}` : ""
        return [x, cm.merged]      
      }
    }
  ))
}

async function saveAccess() {
  // build a a diff between clubdetails and its cooy
  console.log('saving')
  clubdetails.value.clubroles.forEach((c) =>{
    if (c.nature == "ClubAdmin") c.memberlist = Object.keys(clubadmin.value)
    if (c.nature == "InterclubAdmin") c.memberlist = Object.keys(interclubadmin.value)
    if (c.nature == "InterclubCaptain") c.memberlist = Object.keys(clubadmin.value)
  })
  try {
    const reply = await $backend("club", "clb_update_club",{
      clubroles: clubdetails.value.clubroles,
      idclub: props.club.idclub,
      token: idtoken.value,
    })
    statuscm.value = CLUB_STATUS.CONSULTING
    emit('displaySnackbar', t('Club saved'))
    emit('updateClub')
  } catch (error) {
    if (error.code == 401) gotoLogin()
    emit('displaySnackbar', t(error.message))
    return
  }
}


defineExpose({readClubDetails, readClubMembers})
</script>


<template>
  <v-container>
    <p v-if="!club.idclub">{{ $t('Select a club to view the access rights') }}</p>
    <div v-if="club.idclub" class="markdowncontent">
      <v-container v-show="status_consulting">
        <h2>{{ $t('Consulting access rights') }}</h2>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>{{ $t('Club administrators') }}</v-card-title>
              <v-card-text>
                {{ $t('The club administrators have write access to the Club Manager') }}
                <ul>
                  <li v-for="(m, ix) in clubadmin" :key="ix">{{ m }}</li>
                </ul>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>{{ $t('Interclub Administrators') }}</v-card-title>
              <v-card-text>
                {{ $t('The interclub administrators have write access to the Interclub Manager') }}
                <ul>
                  <li v-for="(m, ix) in interclubadmin" :key="ix">{{ m }}</li>
                </ul>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>
                {{ $t('Interclub Captains') }}
              </v-card-title>
              <v-card-text>
                {{ $t('The interclub captains have write access to the planning and ' +
                      'results of the Interclub.')
                }}
                <p>{{ $t('Not available yet') }}</p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row class="ma-2">
          <v-btn @click="modifyAccess">{{ $t('Modify') }}</v-btn>
        </v-row>
      </v-container>
    
      <v-container  v-show="status_modifying">
        <h2 >{{ $t('Modify access rights') }}</h2>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>{{ $t('Club administrators') }}</v-card-title>
              <v-card-text>
                <ul>
                  <li v-for="(m, ix) in clubadmin" :key="m">
                    {{ m }} &nbsp; <v-icon @click="deleteClubAdmin(ix)">mdi-delete</v-icon>
                  </li>
                </ul>
                <v-autocomplete v-model="newclubadmin" :items="props.clubmembers || []" @update:model-value="addClubAdmin"
                  label="Add Member" class="memberselect" item-title="merged" item-value="idnumber">
                </v-autocomplete>              
              </v-card-text>
            </v-card>
          </v-col>        
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>{{ $t('Interclub Administrators') }}</v-card-title>
              <v-card-text>
                <ul>
                  <li v-for="(m, ix) in interclubadmin" :key="m">
                    {{ m }} &nbsp; <v-icon @click="deleteInterclubAdmin(ix)">mdi-delete</v-icon>
                  </li>
                </ul>
                <v-autocomplete v-model="newinterclubadmin" :items="props.clubmembers || []"
                  @update:model-value="addInterclubAdmin" label="Add Member" class="memberselect"  item-title="merged" item-value="idnumber">
                </v-autocomplete>              
              </v-card-text>
            </v-card>
          </v-col>        
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>{{ $t('Club administrators') }}</v-card-title>
              <v-card-text>{{ $t('Not available yet')}}</v-card-text>
            </v-card>
          </v-col>        
        </v-row>
        <v-row class="ma-2">
          <v-btn @click="saveAccess">{{ $t('Save') }}</v-btn>
          <v-btn @click="cancelAccess">{{ $t('Cancel') }}</v-btn>
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
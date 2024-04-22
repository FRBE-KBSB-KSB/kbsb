<script setup>
import { ref, nextTick } from 'vue'
import { VContainer, VBtn, VCard, VCardTitle, VCardText, VCardSubtitle,
  VAlert, VDivider, VAutocomplete } from 'vuetify/lib/components/index.mjs';
import { useIdtokenStore}  from '@/store/idtoken'
import { storeToRefs } from 'pinia'
import { INTERCLUBS_ROUNDS, PLAYERS_DIVISION } from '@/util/interclubs'

// communication with manager
const emit = defineEmits(['displaySnackbar',  'changeDialogCounter'])
defineExpose({ setup })

// idtoken
const idstore = useIdtokenStore()
const { token: idtoken } = storeToRefs(idstore)
const { $backend } = useNuxtApp()

// datamodel
const idclub = ref(0)
let playersindexed = {}
const players = ref([])
const icseries = ref({})
const icclub = ref({})
const round = ref(null)
const teamsplanning = ref({})
const errstatus = ref(null) 

// i18n
const { t: $t } = useI18n()
const { localePath } = useLocalePath()

async function checkAccess(){
  let reply
  emit('changeDialogCounter', 1)
  try {
    reply = await $backend("club", "verify_club_access", {
      idclub: idclub.value,
      role: "InterclubAdmin,InterclubCaptain",
      token: idtoken.value,
    })
    return true
  } catch (error) {
      console.log('reply NOK', error)
      return false
  } finally {
    emit('changeDialogCounter',-1)
  }
}

function clubLabel(pairingnr, s) {
  let name = ""
  s.teams.forEach((t)=>{
    if (t.pairingnumber == pairingnr) {
      name = t.name
      return
    }
  })
  return name
}

async function getICseries() {
  console.log('getICseries')
  let reply
  emit('changeDialogCounter', 1)
  try {
    reply = await $backend("interclub", "clb_getICseries", {
      round: round.value,
      idclub: idclub.value,
      token: idtoken.value
    })
  } catch (error) {
    console.log('NOK', error)
    if (error.code == 401) {
      gotoLogin()
    } 
    return
  } finally {
    emit('changeDialogCounter',-1)
  }
  icseries.value = reply.data
  teamsplanning.value = []
  readICplanning()
}

async function gotoLogin() {
  await navigateTo(localePath('/tools/oldlogin?url=__interclubs__manager'))
}

async function readICclub(){
  players.value = []
  playersindexed.value = {}
  teamsplanning.value = {}
  console.log('icclub', icclub.value)
  icclub.value.players.forEach((p) => {
    if (p.nature !=  "confirmedout") {
      let player = {}
      let tit = p.titular ? `:: ${$t('Titular')} ${p.titular}` : ""
      if (p.nature != "confirmedout") {
        player.first_name = p.first_name
        player.last_name = p.last_name
        player.assignedrating = p.assignedrating
        player.idnumber = p.idnumber
        player.titular = p.titular
        player.full = `${p.idnumber}: ${p.last_name}, ${p.first_name} -- ${p.assignedrating} ${tit}`      
      }
      players.value.push(player)
      playersindexed[p.idnumber] = player   
    }
  })
  console.log('players', players.value)
}

function readICplanning(){
  console.log('readICplanning')
  icseries.value.forEach((s) => {
    // fill in Teams
    s.teams.forEach((t) => {
      let sround = s.rounds[0]
      if(t.idclub == idclub.value) {
        let team = { 
          division: t.division,
          games: [],
          idclub: idclub.value,
          index: s.index,
          pairingnumber: t.pairingnumber,
          name: t.name,
          nrgames: PLAYERS_DIVISION[t.division],
          round: parseInt(round.value),
        }
        let avg = 0
        let allassigned = true
        sround.encounters.forEach((enc, encix) => {
          if (enc.icclub_home == idclub.value && enc.pairingnr_home == t.pairingnumber) {
            team.playinghome = true
            team.idclub_opponent = enc.icclub_visit
            team.name_opponent =  clubLabel(enc.pairingnr_visit, s)
            team.games = enc.games
          }
          else if (enc.icclub_visit == idclub.value && enc.pairingnr_visit == t.pairingnumber) {
            team.playinghome = false
            team.idclub_opponent = enc.icclub_home
            team.name_opponent = clubLabel(enc.pairingnr_home, s)
            team.games = enc.games
          }
        })
        for (let i = team.games.length; i < team.nrgames; i++) {
          team.games[i] = {
            idnumber_home: null,
            idnumber_visit: null,
            result: "",
          } 
        }
        team.games.forEach((g) => {
          if (g.idnumber_home == 0) g.idnumber_home = null
          if (g.idnumber_visit == 0) g.idnumber_visit = null
          if (team.playinghome){
            if (!g.idnumber_home) {
              allassigned = false
            }
            else {
              avg += playersindexed[g.idnumber_home].assignedrating
            }
          }
          else {
            if (!g.idnumber_visit) {
              allassigned = false
            }
            else {
              avg += playersindexed[g.idnumber_visit].assignedrating
            }
          }
          team.average = allassigned ? avg / team.nrgames : 0
        })
        // do nothing it for BYE
        if (team.idclub_opponent) teamsplanning.value.push(team)
      } 
    })
  })
}

async function savePlanning(){
  let reply
  console.log('saving planning', teamsplanning.value)
  try {
    emit('changeDialogCounter', 1)
		reply = await $backend("interclub","clb_saveICplanning", {
      token: idtoken.value,
      plannings: teamsplanning.value
		})
  } catch (error) {
    if (error.code == 401) gotoLogin()
    emit('displaySnackbar', t(error.message))
    return
  }
  finally {
    emit('changeDialogCounter',-1)
  }
	emit('displaySnackbar', t('Playerlist saved'))
  getICseries()
}

async function setup(clb, rnd){
  console.log('setup planning', clb, rnd)
  errstatus.value = null
  icclub.value = clb
  round.value = rnd
  idclub.value = clb.idclub
  if (!idclub.value) {
    errstatus.value = 'noclub'
    players.value = []
    playersindexed = {}
    icseries.value = {}
    return
  }
  let ca = await checkAccess()
  console.log('ca', ca)
  if (!ca) {
    errstatus.value = 'noaccess'
    players.value = []
    playersindexed = {}
    icseries.value = {}
    return
  }
  readICclub()
  const now = new Date().valueOf()
  const expiry = new Date(INTERCLUBS_ROUNDS[round.value] + 'T14:00').valueOf()
  console.log('dates', new Date(), new Date(INTERCLUBS_ROUNDS[round.value] + 'T14:00'))
  if (now > expiry) {
    errstatus.value = 'expired'
    players.value = []
    playersindexed = {}
    icseries.value = {} 
    return   
  }
  nextTick(()=>{
    getICseries()
  })
}

function validatePlanning(){
  let reply
  savePlanning()
}

</script>
<template>
	<v-container>
    <div v-if="errstatus=='noclub'">
      <v-alert  type="warning" variant="outlined" closable 
        :text="$t('Please select a club')"/>
    </div>
    <div v-if="errstatus=='noaccess'">
      <v-alert  type="error" variant="outlined" closable 
        :text="$t('Permission denied')"/>
    </div>
    <div v-if="errstatus=='expired'">
      <v-alert  type="warning" variant="outlined" closable 
        :text="$t('You can no longer modify the planning of this round')"/>
    </div>
    <div v-if="!errstatus">
      <VCard v-for="(tp,ix) in teamsplanning" class="my-2">
        <VCardTitle>
          {{ tp.name }}
        </VCardTitle>
        <VCardSubtitle class="d-flex">
          <div v-show="tp.playinghome" class="flex-1-1-100">
            {{  tp.idclub }} {{tp.name}} - {{ tp.idclub_opponent  }} {{ tp.name_opponent }}
          </div>
          <div v-show="!tp.playinghome" class="flex-1-1-100">
            {{ tp.idclub_opponent  }} {{ tp.name_opponent }} - {{  tp.idclub }} {{tp.name}}
          </div>
          <div class="flex-0-0" >
            {{ $t('Average ELO') }}: {{ tp.average }}
          </div>
          <VDivider />
        </VCardSubtitle>
        <VCardText>
          <div v-for="(g,ix) in tp.games">
            <VAutocomplete v-model="g.idnumber_home" density="compact" 
                :items="players" item-title="full" item-value="idnumber" 
                :label="$t('Player')+ ' ' + (ix +1)" :hide-details="true" 
                v-show="tp.playinghome" clearable
            />
            <VAutocomplete v-model="g.idnumber_visit" density="compact" 
                :items="players" item-title="full" item-value="idnumber" 
                :label="$t('Player') + ' ' +  (ix +1)" :hide-details="true" 
                v-show="!tp.playinghome" clearable
            />
          </div>
        </VCardText>
      </VCard>
      <div v-show="icseries.length">
        <VBtn @click="validatePlanning()" color="primary">{{ $t('Save') }}</VBtn>
      </div>
    </div>          
  </v-container>

</template>

<style scoped>
.imported {
  color: purple;
  font-weight: 500;
}
.exported {
  color: rgb(186, 185, 185);
}

</style>

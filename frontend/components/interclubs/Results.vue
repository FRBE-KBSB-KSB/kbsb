<script setup>
import { ref, nextTick } from 'vue'
import { useIdtokenStore } from '@/store/idtoken'
import { useIdnumberStore } from '@/store/idnumber'
import { storeToRefs } from 'pinia'
import { INTERCLUBS_ROUNDS, PLAYERS_DIVISION, resultchoices } from '@/util/interclubs'

// communication with manager
const emit = defineEmits(['displaySnackbar', 'changeDialogCounter'])
defineExpose({ setup })

// idtoken
const idstore = useIdtokenStore()
const { token: idtoken } = storeToRefs(idstore)
const idnstore = useIdnumberStore()
const { idnumber: idn } = storeToRefs(idnstore)
const { $backend } = useNuxtApp()

// datamodel
const idclub = ref(0)
const icclub = ref({})
const playerlist_buffer = ref({})
let playersindexed = {}
const icseries = ref([])
const round = ref(-1)
const teamresults = ref([])
const errstatus = ref(null)

// i18n
const { t } = useI18n()

// methods alphabetically

function calc_points(enc) {
  let bphome = 0
  let bpvisit = 0
  let allfilled = true
  let teamforfeit = false
  enc.games.forEach((g) => {
    let result = isOverruled(g) ? g.overruled : g.result
    switch (result) {
      case "1-0":
      case "1-0 FF":
        bphome += 2
        break
      case "½-½":
        bphome += 1
        bpvisit += 1
        break
      case "½-0":
        bphome += 1
        break
      case "0-½":
        bpvisit += 1
        break
      case "0-1":
      case "0-1 FF":
        bpvisit += 2
        break
      case "Team FF":
        teamforfeit = true
        break
      case "":
        allfilled = false
        break;
    }
  })
  enc.boardpoints = `${bphome / 2}-${bpvisit / 2}`
  if (!allfilled) {
    enc.matchpoints = ""
  }
  else if (teamforfeit) {
    enc.matchpoints = "TFF"
  }
  else {
    if (bphome > bpvisit) enc.matchpoints = "2-0"
    if (bphome == bpvisit) enc.matchpoints = "1-1"
    if (bphome < bpvisit) enc.matchpoints = "0-2"
  }
}

async function checkAccess() {
  emit('changeDialogCounter', 1)
  try {
    await $backend("club", "verify_club_access", {
      idclub: idclub.value,
      role: "InterclubAdmin,InterclubCaptain",
      token: idtoken.value,
    })
    return true
  } catch (error) {
    return false
  } finally {
    emit('changeDialogCounter', -1)
  }
}

function clubLabel(pairingnr, teams) {
  let name = ""
  teams.forEach((t) => {
    if (t.pairingnumber == pairingnr) {
      name = t.name
      return
    }
  })
  return name
}

function getICplayerlist(ic_clb) {
  if (!ic_clb && !ic_clb.idclub) return
  let players = ic_clb.players.filter((p) => p.nature != "confirmedout")
  playerlist_buffer.value[ic_clb.idclub] = players
  players.forEach((p) => {
    p.full = `${p.idnumber} ${p.last_name}, ${p.first_name}`
    playersindexed[p.idnumber] = p
  })
}

async function getICclub(clb_id) {
  if (playerlist_buffer.value[clb_id]) {
    return
  }
  let reply
  emit('changeDialogCounter', 1)
  try {
    reply = await $backend("interclub", "anon_getICclub", {
      idclub: clb_id
    })
  } catch (error) {
    displaySnackbar(t(error.message))
    return
  }
  finally {
    emit('changeDialogCounter', -1)
  }
  let cl = reply.data
  getICplayerlist(cl)
}

async function getICSeries() {
  let reply
  if (!idclub.value) {
    icseries.value = {}
    return
  }
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
    emit('changeDialogCounter', -1)
  }
  icseries.value = reply.data
  await readICSeries()
}

async function gotoLogin() {
  await navigateTo(localePath('/tools/oldlogin?url=__interclubs__manager'))
}


function isOverruled(game) {
  return game.overruled && game.overruled != "NOR"
}

async function readICSeries() {
  let tra = []
  teamresults.value = []
  icseries.value.forEach((s) => {
    const { division, index } = s
    s.rounds[0].encounters.forEach(function (enc) {
      if (enc.icclub_home && enc.icclub_visit) {   // skip byes
        if ((enc.icclub_home == idclub.value) || (enc.icclub_visit == idclub.value)) {
          getICclub(enc.icclub_home)
          getICclub(enc.icclub_visit)
          let tr = {
            division: division,
            games: enc.games,
            icclub_home: enc.icclub_home,
            icclub_visit: enc.icclub_visit,
            index: index,
            name_home: clubLabel(enc.pairingnr_home, s.teams),
            name_visit: clubLabel(enc.pairingnr_visit, s.teams),
            nrgames: PLAYERS_DIVISION[division],
            pairingnr_home: enc.pairingnr_home,
            pairingnr_visit: enc.pairingnr_visit,
            round: round.value,
            signhome_idnumber: enc.signhome_idnumber,
            signhome_ts: enc.signhome_ts,
            signvisit_idnumber: enc.signvisit_idnumber,
            signvisit_ts: enc.signvisit_ts,
          }
          for (let i = tr.games.length; i < tr.nrgames; i++) {
            tr.games[i] = {
              idnumber_home: null,
              idnumber_visit: null,
              result: "",
            }
          }
          tr.games.forEach((g) => {
            if (g.idnumber_home == 0) g.idnumber_home = null
            if (g.idnumber_visit == 0) g.idnumber_visit = null
          })
          calc_points(tr)
          tra.push(tr)
        }
      }
    })
  })
  tra = tra.sort((a, b) => (a.division - b.division))
  teamresults.value = [...tra]
}

async function saveResults() {
  let reply
  try {
    emit('changeDialogCounter', 1)
    reply = await $backend("interclub", "clb_saveICresults", {
      token: idtoken.value,
      results: teamresults.value
    })
  } catch (error) {
    emit('displaySnackbar', t(error.message))
    return
  }
  finally {
    emit('changeDialogCounter', -1)
  }
  emit('displaySnackbar', t('Results saved'))
}

async function setup(clb, rnd) {
  console.log('setup results', clb, rnd)
  errstatus.value = null
  icclub.value = clb
  round.value = rnd
  idclub.value = clb.idclub
  if (!idclub.value) {
    errstatus.value = 'noclub'
    playerlist_buffer.value = {}
    teamresults.value = []
    icseries.value = []
    return
  }
  let ca = await checkAccess()
  if (!ca) {
    errstatus.value = 'noaccess'
    playerlist_buffer.value = {}
    teamresults.value = []
    icseries.value = []
    return
  }
  const now = new Date().valueOf()
  const opened = new Date(INTERCLUBS_ROUNDS[round.value] + 'T15:00').valueOf()
  const closed = opened + 3600000 * (9 + 24)
  console.log('dates', new Date(), new Date(INTERCLUBS_ROUNDS[round.value] + 'T15:00'))
  if (now < opened) {
    errstatus.value = 'notopenyet'
    playerlist_buffer.value = {}
    teamresults.value = []
    icseries.value = []
    return
  }
  if (now > closed) {
    errstatus.value = 'closed'
    playerlist_buffer.value = {}
    teamresults.value = []
    icseries.value = []
    return
  }
  if (!playerlist_buffer[idclub.value]) {
    getICplayerlist(clb)
  }
  getICSeries()
}


function sign(tr, who) {
  let plinpll = false
  console.log('tr', tr)
  if (who == "home") {
    const clb = tr.icclub_home
    console.log('clb', clb, "idn", idn.value)
    playerlist_buffer.value[clb].forEach((p) => {
      if (p.idnumber == idn.value) {
        console.log('idn belongs to club home')
        plinpll = true
      }
    })
    if (!plinpll && idn.value < 200000) {
      console.error('idn not in club home')
      return
    }
    tr.signhome_idnumber = idn
    tr.signhome_ts = new Date().toISOString()
  }
  else {
    const clb = tr.icclub_visit
    playerlist_buffer.value[clb].forEach((p) => {
      if (p.idnumber == idn.value) {
        console.log('idn belongs to club visit')
        plinpll = true
      }
    })
    if (!plinpll && idn.value < 200000) {
      console.error('idn not in club visit')
      return
    }
    tr.signvisit_idnumber = idn
    tr.signvisit_ts = new Date().toISOString()
  }
}

</script>

<template>
  <v-container>
    <div v-if="errstatus == 'noclub'">
      <v-alert type="warning" variant="outlined" closable :text="t('Please select a club')" />
    </div>
    <div v-if="errstatus == 'noaccess'">
      <v-alert type="error" variant="outlined" closable :text="t('Permission denied')" />
    </div>
    <div v-if="errstatus == 'notopenyet'">
      <v-alert type="warning" variant="outlined" closable
        :text="t('Entry of the results starts on Sunday at 15h')" />
    </div>
    <div v-if="errstatus == 'closed'">
      <v-alert type="warning" variant="outlined" closable
        :text="t('You can no longer modify the results')" />
    </div>
    <div v-if="!errstatus">
      <VBtn color="green" @click="saveResults">{{ t('Save results') }}</VBtn>
      <v-card v-for="tr in teamresults" class="my-2">
        <v-card-title>
          {{ t('Division') }} {{ tr.division }}{{ tr.index }}: &nbsp;
          {{ tr.icclub_home }} {{ tr.name_home }} -
          {{ tr.icclub_visit }} {{ tr.name_visit }}
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-row v-for="(g, ix) in tr.games" class="d-flex">
              <v-col cols="4">
                <VAutocomplete v-model="g.idnumber_home" density="compact" clearable
                  :items="playerlist_buffer[tr.icclub_home]" item-title="full" item-value="idnumber"
                  :label="t('Player home') + ' ' + (ix + 1)" :hide-details="true" />
              </v-col>
              <v-col cols="2">
                <VSelect v-model="g.result" :items="resultchoices" density="compact"
                  :hide-details="true" @update:model-value="calc_points(tr)" />
              </v-col>
              <v-col cols="4">
                <VAutocomplete v-model="g.idnumber_visit" density="compact"
                  :items="playerlist_buffer[tr.icclub_visit]" item-title="full"
                  item-value="idnumber" :label="t('Player visit') + ' ' + (ix + 1)"
                  :hide-details="true" clearable />
              </v-col>
              <v-col col="2">
                <div v-show="isOverruled(g)" class="text-purple font-weight-bold">
                  {{ g.overruled }}
                </div>
              </v-col>
            </v-row>
            <VDivider />
            <v-row class="mt-1">
              <v-col col="4" v-show="tr.matchpoints && tr.signhome_idnumber">
                {{ t('signature') }} {{ t('home') }}: {{ tr.signhome_idnumber }}
              </v-col>
              <v-col col="4" v-show="tr.matchpoints && !tr.signhome_idnumber">
                {{ t('home') }}
                <v-btn @click="sign(tr, 'home')" color="green" density="compact">{{ t('sign')
                  }}</v-btn>
              </v-col>
              <v-col cols="2">
                MP: {{ tr.matchpoints }}
              </v-col>
              <v-col cols="2">
                BP: {{ tr.boardpoints }}
              </v-col>
              <v-col col="4" v-show="tr.matchpoints && tr.signvisit_idnumber">
                {{ t('signature') }} {{ t('away') }}: {{ tr.signvisit_idnumber }}
              </v-col>
              <v-col col="4" v-show="tr.matchpoints && !tr.signvisit_idnumber">
                {{ t('away') }}
                <v-btn @click="sign(tr, 'away')" color="green" density="compact">{{ t('sign')
                  }}</v-btn>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
      <VBtn color="green" @click="saveResults">{{ t('Save results') }}</VBtn>
    </div>

  </v-container>
</template>

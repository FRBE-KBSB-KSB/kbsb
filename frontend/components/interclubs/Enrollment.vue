<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useIdtokenStore } from '@/store/idtoken'
import { storeToRefs } from 'pinia'

// communication
defineExpose({ setup })
const idstore = useIdtokenStore()
const { token: idtoken } = storeToRefs(idstore)
const { $backend } = useNuxtApp()
const { t } = useI18n()

//  snackbar and loading widgets
import ProgressLoading from '@/components/ProgressLoading.vue'
import SnackbarMessage from '@/components/SnackbarMessage.vue'
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

// datamodel
const empty_enrollment = {
  teams1: 0,
  teams2: 0,
  teams3: 0,
  teams4: 0,
  teams5: 0,
  wishes: {},
};
const enrollment = ref({ ...empty_enrollment})
const enr_status = ref('closed')
const modifying = ref(false)
const grouping = ref([
  { "title": t("icn.nopref"), "value": "0" },
  { "title": t("icn.1group"), "value": "1" },
  { "title": t("icn.2groups"), "value": "2" },
])
const splitting = ref([
  { "title": t("icn.1series"), "value": "1" },
  { "title": t("icn.mult_series"), "value": "2" },
])

const rules = ref({
  count20: (x) => (x && x.length <= 20 || 'Max 20 characters')
})
let icclub = {}
let icdata = {}

// computed
const splittingvalue = computed(()=>{
  let sp = splitting.value[0].title
  const val = enrollment.value.wishes.splitting || "2"
  splitting.value.forEach(e => {
    if (e.value == val) {
      sp = e.title
    }
  });
  return sp  
})
const groupingvalue = computed(()=>{
  let gr = grouping.value[0].title
  const val = enrollment.value.wishes.grouping || "0"
  grouping.value.forEach(e => {
    if (e.value == val) {
      gr = e.title
    }
  });
  return gr  
})

// methods 

async function cancelEnrollment() {
  enr_status.value = 'open'
  await find_interclubenrollment()
}

function calcstatus(){
  // we have the following status
  // - open
  // - closed
  // - noclub
  // - editing
  // - noaccess
  enr_status.value = 'closed'
  if (!icclub.id) {
    enr_status.value = 'noclub'
    return
  }
  if (modifying.value) {
    enr_status.value = 'editing'
    return
  }
  // TODO date check
  enr_status.value = 'open'
}

async function checkAccess() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("club", "verify_club_access", {
      idclub: icclub.idclub,
      role: "InterclubAdmin,InterclubCaptain",
      token: idtoken.value,
    })
    return true
  } catch (error) {
    console.log('reply NOK', error)
    enr_status.value = 'noaccess'
    showSnackbar(t('icn.perm_denied'))
    return false
  } finally {
    showLoading(false)
  }
}

async function find_interclubenrollment() {
  if (!icclub.idclub) return
  let reply
  enrollment.value = { ...empty_enrollment }
  showLoading(true)
  try {
    reply = await $backend("interclub", "find_interclubenrollment", {
        idclub: icclub.idclub
    })
    readEnrollment(reply.data)
  } 
  catch (error) {
    console.log('NOK find_interclubenrollment', error)
    if (error.code == 401) {
      gotoLogin()
    }
    else {
      showSnackbar(t('Getting existing enrollment failed'))
    }
    return
  }
  finally {
    showLoading(false)
  }
}

async function gotoLogin() {
  await router.push('/tools/oldlogin?url=__interclubs__manager')
}

async function modifyEnrollment() {
  if (! modifying.value) {
    const allowed = await checkAccess()
    if (allowed) {
      modifying.value = true
    }
  }
  else {
    modifying.value = false
  }
  calcstatus()
}

function readEnrollment(data){
  if (data) {
    enrollment.value = data
  }
  else {
      enrollment.value.id = null
  }
  if (!enrollment.value.name || !enrollment.value.name.length) {
    enrollment.value.name = icclub.name
  }
  if (!enrollment.value.wishes.grouping) {
    enrollment.value.wishes.grouping = "0"
  }
  if (!enrollment.value.wishes.splitting) {
    enrollment.value.wishes.splitting = "2"
  }
  console.log('enr', enrollment.value)
}


async function saveEnrollment() {
  let reply
  showLoading(true)

  try {
      reply = await $backend("interclub", "set_interclubenrollment", {
        idclub: icclub.idclub,
        token: idtoken.value,
        name: enrollment.value.name,
        teams1: enrollment.value.teams1,
        teams2: enrollment.value.teams2,
        teams3: enrollment.value.teams3,
        teams4: enrollment.value.teams4,
        teams5: enrollment.value.teams5,
        wishes: enrollment.value.wishes,        
      })
      modifying.value = false
      calcstatus()
      showSnackbar(t('icn.save_enr_ok'))      
  } 
  catch (error) {
    console.log('NOK set_interclubenrollment', error)
    if (error.code == 401) {
      gotoLogin()
    }
    else {
      showSnackbar(t('enc.save_enr_fail'))      
    }
    return
  }
  finally {
    showLoading(false)
    await find_interclubenrollment()
  }  
}

async function setup(icclub_, icdata_) {
  console.log('setup Enrollment', icclub_, icdata_)
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading  
  icclub = icclub_
  icdata = icdata_
  calcstatus()
  await find_interclubenrollment()
}

</script>

<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />      
    <v-alert type="warning" variant="outlined" v-if="enr_status == 'closed'"
      :text="t('icn.enr_closed')" />
    <v-alert type="warning" variant="outlined" v-if="enr_status == 'noclub'"
      :text="t('icn.select_club')" />
    <v-alert type="error" variant="outlined" v-if="enr_status == 'noaccess'"
      :text="t('icn.perm_denied')" />   
    <div v-if="enr_status == 'open'">
      <v-row v-show="!enrollment.id">
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{ $t("icn.enr") }}
            </v-card-title>
            <v-card-text>
              {{ $t('icn.not_enrolled') }}
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row v-show="enrollment.id">
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{ $t("icn.teams") }}
            </v-card-title>
            <v-card-text>
              <ul>
                <li>{{ $t('icn.teams_div') }} 1: {{ enrollment.teams1 }}
                </li>
                <li>{{ $t('icn.teams_div') }} 2: {{ enrollment.teams2 }}
                </li>
                <li>{{ $t('icn.teams_div') }} 3: {{ enrollment.teams3 }}
                </li>
                <li>{{ $t('icn.teams_div') }} 4: {{ enrollment.teams4 }}
                </li>
                <li>{{ $t('icn.teams_div') }} 5: {{ enrollment.teams5 }}
                </li>
              </ul>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{ $t("icn.wishes") }}
            </v-card-title>
            <v-card-text>
              <ul>
                <li>{{ $t('icn.teams_grouped') }}: {{ groupingvalue }}</li>
                <li>{{ $t('icn.teams_distr') }}: 
                  {{ splittingvalue }} </li>
                <li>{{ $t('icn.reg_pref') }}: 
                  {{ enrollment.wishes.regional }} </li>
                <li>{{ $t('Remarks') }}: {{ enrollment.wishes.remarks }} </li>
              </ul>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{ $t("Name") }}
            </v-card-title>
            <v-card-text>
              {{ $t('icn.name_club') }}: 
              {{enrollment.name }}
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-btn @click="modifyEnrollment">
          {{ $t('Edit') }}
        </v-btn>
      </v-row>
    </div>
    <div v-if="enr_status == 'editing'">
      <v-row>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{ t('icn.teams') }}
            </v-card-title>
            <v-card-text>
              <p>{{ t('icn.teams_nb_div') }}</p>
              <v-text-field v-model="enrollment.teams1" :label="t('icn.div') + ' 1'"
                type="number" min="0" max="1" />
              <v-text-field v-model="enrollment.teams2" :label="t('icn.div') + ' 2'"
                type="number" min="0" max="15" />
              <v-text-field v-model="enrollment.teams3" :label="t('icn.div') + ' 3'"
                type="number" min="0" max="15" />
              <v-text-field v-model="enrollment.teams4" :label="t('icn.div') + ' 4'"
                type="number" min="0" max="15" />
              <v-text-field v-model="enrollment.teams5" :label="t('icn.div') + ' 5'"
                type="number" min="0" max="15" />
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{ t('icn.wishes') }}
            </v-card-title>
            <v-card-text>
              <div>{{ t('icn.teams_grouped') }}</div>
              <v-select :label="t('icn.grouping')" v-model="enrollment.wishes.grouping"
                :items="grouping" />
              <div>{{ t('icn.teams_distr') }}</div>
              <v-select :label="t('icn.dist')" v-model="enrollment.wishes.splitting"
                :items="splitting" />
              <div>{{ t('icn.reg_pref') }}</div>
              <v-text-field v-model="enrollment.wishes.regional" :label="t('Regional')" />
              <v-textarea rows="5" v-model="enrollment.wishes.remarks"
                :label="t('icn.other_wishes')" />
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" xl="3">
          <v-card class="elevation-5">
            <v-card-title class="card-title">
              {{ t('Name') }}
            </v-card-title>
            <v-card-text>
              {{ t('icn.team_name') }}
              <v-text-field v-model="enrollment.name" :label="$t('Name')" maxlength="20"
                :rules="[rules.count20]" />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-btn @click="saveEnrollment">
          {{ t('Save') }}
        </v-btn>&nbsp;
        <v-btn @click="cancelEnrollment">
          {{ t('Cancel') }}
        </v-btn>
      </v-row>
    </div>
  </v-container>
</template>

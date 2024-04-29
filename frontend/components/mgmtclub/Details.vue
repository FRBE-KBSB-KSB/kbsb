<script setup>
import { ref, computed } from 'vue'

import { CLUB_STATUS, EMPTY_CLUB } from '@/util/club'
import showdown from 'showdown'

// stores
import { useMgmtTokenStore } from "@/store/mgmttoken"
import { storeToRefs } from 'pinia'
const mgmtstore = useMgmtTokenStore()
const { token: mgmttoken } = storeToRefs(mgmtstore)

// communication
const emit = defineEmits(['updateClub'])
defineExpose({ setup })
const { $backend } = useNuxtApp()

//  snackbar and loading widgets
import ProgressLoading from '@/components/ProgressLoading.vue'
import SnackbarMessage from '@/components/SnackbarMessage.vue'
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

// datamodel
const clubdetails = ref(EMPTY_CLUB)
const helpdialog = ref(false)
const statuscm = ref(CLUB_STATUS.CONSULTING)
const status_consulting = computed(() => (statuscm.value == CLUB_STATUS.CONSULTING))
const status_modifying = computed(() => (statuscm.value == CLUB_STATUS.MODIFYING))
const mdConverter = new showdown.Converter()
let copyclubdetails = null


function cancelClub() {
  statuscm.value = CLUB_STATUS.CONSULTING
}


async function modifyClub() {
  statuscm.value = CLUB_STATUS.MODIFYING
}

function readClubDetails(club) {
  console.log('readClubDetails in details')
  clubdetails.value = { ...EMPTY_CLUB, ...club }
  copyclubdetails = JSON.parse(JSON.stringify(club))
}

async function saveClub() {
  // build a a diff between clubdetails and its cooy
  console.log('saveClub')
  let update = {}
  for (const [key, value] of Object.entries(clubdetails.value)) {
    if (value != copyclubdetails[key]) {
      update[key] = value
    }
  }
  showLoading(true)
  try {
    const reply = await $backend("club", "mgmt_update_club", {
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

function setup(club) {
  console.log('setupDetails', club)
  readClubDetails(club)
}

onMounted(() => {
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
})
</script>


<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <p v-if="!clubdetails.idclub">Select a club to view the club details</p>
    <div v-if="clubdetails.idclub">
      <v-container v-show="status_consulting">
        <h2>Consulting club details</h2>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>
                Club details
              </v-card-title>
              <v-card-text>
                <div><span class="fieldname">Long name</span>: {{ clubdetails.name_long }}
                </div>
                <div><span class="fieldname">Short name</span>: {{ clubdetails.name_short }}
                </div>
                <div><span class="fieldname">Federation</span>: {{ clubdetails.federation }}
                </div>
                <div><span class="fieldname">Website</span>: {{ clubdetails.website }}</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>Bank details</v-card-title>
              <v-card-text>
                <div><span class="fieldname">Bank account name</span>: {{
      clubdetails.bankaccount_name
    }}
                </div>
                <div><span class="fieldname">Bank account IBAN</span>: {{
        clubdetails.bankaccount_iban
      }}
                </div>
                <div><span class="fieldname">Bank account BIC</span>: {{
        clubdetails.bankaccount_bic
      }}
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title class="mt-2">
                <v-btn icon="mdi-help" color="purple" size="small" class="float-right"
                  @click="helpdialog = true" />
                <h4>{{ $t('Contact') }}</h4>
              </v-card-title>
              <v-card-text>
                <div><span class="fieldname">Main email address</span>: {{
      clubdetails.email_main
    }}
                </div>
                <div><span class="fieldname">Email address Interclub</span>: {{
        clubdetails.email_interclub
      }}</div>
                <div><span class="fieldname">Email address administration</span>: {{
        clubdetails.email_admin
      }}</div>
                <div><span class="fieldname">Email address finance</span>: {{
        clubdetails.email_finance
      }}
                </div>
                <div><span class="fieldname">Postal address</span>:<br />
                  <span v-html='clubdetails.address.replaceAll("\n", "<br />")'></span>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>
                Playing details
              </v-card-title>
              <v-card-text>
                <div><span class="fieldname">Club venue</span>:<br />
                  <span v-html='clubdetails.venue.replaceAll("\n", "<br />")'></span>
                </div>
                <h4>Playing hours</h4>
                <div v-for="(h, d) in clubdetails.openinghours" :key="d">
                  <div v-show="h.length">
                    <span class="fieldname">d</span>: {{ h }}
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row class="mt-2">
          <v-btn @click="modifyClub">Modify</v-btn>
        </v-row>
      </v-container>
      <v-container v-show="status_modifying">
        <h2>Modify club details</h2>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card class="elevation-5">
              <v-card-title>
                Club details
              </v-card-title>
              <v-card-text>
                <v-text-field v-model="clubdetails.name_long" label="Long name" />
                <v-text-field v-model="clubdetails.name_short" label="Short name" />
                <p>Federation: {{ clubdetails.federation }}</p>
                <v-text-field v-model="clubdetails.website" label="Website" />
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card class="elevation-5">
              <v-card-title>
                Contact
              </v-card-title>
              <v-card-text>
                <v-text-field v-model="clubdetails.email_main" label="Main email address" />
                <v-text-field v-model="clubdetails.email_interclub"
                  label="Email address Interclub" />
                <v-text-field v-model="clubdetails.email_admin"
                  label="Email address administration" />
                <v-text-field v-model="clubdetails.email_finance" label="Email address finance" />
                <v-textarea rows="3" v-model="clubdetails.address" label="Postal address" />
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card class="elevation-5">
              <v-card-title>
                {{ $t('Bank details') }}
              </v-card-title>
              <v-card-text>
                <v-text-field v-model="clubdetails.bankacount_name" label="Bank account name" />
                <v-text-field v-model="clubdetails.bankaccount_iban" label="Bank account IBAN" />
                <v-text-field v-model="clubdetails.bankaccount_bic" label="Bank account BIC" />
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>
                {{ $t('Playing details') }}
              </v-card-title>
              <v-card-text>
                <v-textarea rows="3" v-model="clubdetails.venue" label="Club venue" />
                <h4>{{ $t('Playing hours') }}</h4>
                <v-text-field v-model="clubdetails.openinghours.Monday" label="Monday" />
                <v-text-field v-model="clubdetails.openinghours.Tuesday" label="Tuesday" />
                <v-text-field v-model="clubdetails.openinghours.Wednesday" label="Wednesday" />
                <v-text-field v-model="clubdetails.openinghours.Thursday" label="Thursday" />
                <v-text-field v-model="clubdetails.openinghours.Friday" label="Friday" />
                <v-text-field v-model="clubdetails.openinghours.Saturday" label="Saturday" />
                <v-text-field v-model="clubdetails.openinghours.Sunday" label="Sunday" />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row class="ma-2">
          <v-btn @click="saveClub">Save</v-btn>
          <v-btn @click="cancelClub">Cancel</v-btn>
        </v-row>
      </v-container>
    </div>
    <v-dialog v-model="helpdialog" width="20em">
      TODO
    </v-dialog>
  </v-container>
</template>

<style scoped>
.fieldname {
  color: purple;
}
</style>

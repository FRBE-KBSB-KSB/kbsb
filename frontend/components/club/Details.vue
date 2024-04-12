<script setup>
import { ref, computed, nextTick } from 'vue'
import { CLUB_STATUS, EMPTY_CLUB } from '@/util/club'
import { VContainer, VBtn, VCard, VCardTitle, VCardText, VDialog, VRow, VCol,
  VTextField,VTextarea, VDivider } from 'vuetify/lib/components/index.mjs';

import { useIdtokenStore}  from '@/store/idtoken'
import { storeToRefs } from 'pinia'
import showdown from 'showdown'

const { localePath } = useLocalePath()
const { locale, t } = useI18n()
const { $backend } = useNuxtApp()
const props = defineProps(['club'])
const clubdetails = ref(EMPTY_CLUB)
const helpdialog = ref(false)
const statuscm = ref(CLUB_STATUS.CONSULTING)
const idstore = useIdtokenStore()
const { token: idtoken } = storeToRefs(idstore)
const { data: help }  = await useAsyncData('help-login', () => queryContent('/pages/help-club-contact').findOne())
const status_consulting = computed(() => (statuscm.value == CLUB_STATUS.CONSULTING))
const status_modifying = computed(() => (statuscm.value == CLUB_STATUS.MODIFYING))
const mdConverter = new showdown.Converter()
const ttitle = `title_${locale.value}`
const tcontent = `content_${locale.value}`
let copyclubdetails = null
const emit = defineEmits(['displaySnackbar', 'updateClub'])

function md(s) { 
  return  mdConverter.makeHtml(s)
}

function cancelClub() {
  statuscm.value = CLUB_STATUS.CONSULTING
  emit('updateClub')
}


function gotoLogin() {
  navigateTo(localePath('/tools/login?url=__clubs__manager'))
}

async function modifyClub() {
  statuscm.value = CLUB_STATUS.MODIFYING
}

function readClubDetails() {
  console.log('details.clubdetails', props.club)
  clubdetails.value = { ...EMPTY_CLUB, ...props.club }
  copyclubdetails = JSON.parse(JSON.stringify(props.club))
}

async function saveClub() {
  // build a a diff between clubdetails and its cooy
  let update = {}
  for (const [key, value] of Object.entries(clubdetails.value)) {
    if (value != copyclubdetails[key]) {
      update[key] = value
    }
  }
  try {
    const reply = await $backend("club", "clb_update_club",{
      ...update,
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


defineExpose({readClubDetails})


</script>


<template>
  <v-container>
    <p v-if="!club.idclub">{{ $t('Select a club to view the club details') }}</p>
    <div v-if="club.idclub">
      <v-container v-show="status_consulting">
        <h2>{{ $t('Consulting club details') }}</h2>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>            
              <v-card-title>
                {{ $t('Club details') }}
              </v-card-title>
              <v-card-text>
                <div><span class="fieldname">{{ $t('Long name') }}</span>: {{ clubdetails.name_long }}
                </div>
                <div><span class="fieldname">{{ $t('Short name') }}</span>: {{ clubdetails.name_short }}
                </div>
                <div><span class="fieldname">{{ $t('Federation') }}</span>: {{ clubdetails.federation }}
                </div>
                <div><span class="fieldname">{{ $t('Website') }}</span>: {{ clubdetails.website }}</div>              
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>{{ $t('Bank details') }}</v-card-title>
              <v-card-text>
                <div><span class="fieldname">{{ $t('Bank account name') }}</span>: {{
                  clubdetails.bankaccount_name
                }}
                </div>
                <div><span class="fieldname">{{ $t('Bank account IBAN') }}</span>: {{
                  clubdetails.bankaccount_iban
                }}
                </div>
                <div><span class="fieldname">{{ $t('Bank account BIC') }}</span>: {{
                  clubdetails.bankaccount_bic
                }}
                </div>              
              </v-card-text>
            </v-card>
          </v-col>                      
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title class="mt-2">
                <v-btn icon="mdi-help" color="green" size="small" class="float-right" @click="helpdialog = true"/>                
                <h4>{{ $t('Contact') }}</h4>
              </v-card-title>
              <v-card-text>
                <div><span class="fieldname">{{ $t('Main email address') }}</span>: {{
                  clubdetails.email_main
                }}
                </div>
                <div><span class="fieldname">{{ $t('Email address Interclub') }}</span>: {{
                  clubdetails.email_interclub
                }}</div>
                <div><span class="fieldname">{{ $t('Email address administration') }}</span>: {{
                  clubdetails.email_admin
                }}</div>
                <div><span class="fieldname">{{ $t('Email address finance') }}</span>: {{
                  clubdetails.email_finance
                }}
                </div>
                <div><span class="fieldname">{{ $t('Postal address') }}</span>:<br />
                  <span v-html='clubdetails.address.replaceAll("\n", "<br />")'></span>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>
                {{ $t('Playing details') }}
              </v-card-title>
              <v-card-text>
                <div><span class="fieldname">{{ $t('Club venue') }}</span>:<br />
                  <span v-html='clubdetails.venue.replaceAll("\n", "<br />")'></span>
                </div>
                <h4>{{ $t('Playing hours') }}</h4>
                <div v-for="(h,d) in clubdetails.openinghours" :key="d">
                  <div v-show="h.length">
                    <span class="fieldname">{{ $t(d)  }}</span>: {{ h }}
                  </div>
                </div>                
              </v-card-text>
            </v-card>
          </v-col> 
        </v-row>
        <v-row class="mt-2">
          <v-btn @click="modifyClub">{{ $t('Modify') }}</v-btn>
        </v-row>
      </v-container>
      <v-container v-show="status_modifying">
        <h2>{{ $t('Modify club details') }}</h2>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card class="elevation-5">
              <v-card-title>
                {{ $t('Club details') }}
              </v-card-title>
              <v-card-text>
                <v-text-field v-model="clubdetails.name_long" :label="$t('Long name')" />
                <v-text-field v-model="clubdetails.name_short" :label="$t('Short name')" />
                <p>{{ $t('Federation') }}: {{ clubdetails.federation }}</p>
                <v-text-field v-model="clubdetails.website" label="Website" />
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card class="elevation-5">
              <v-card-title>
                {{ $t('Contact') }}
              </v-card-title>
              <v-card-text>
                <v-text-field v-model="clubdetails.email_main" :label="$t('Main email address')" />
                <v-text-field v-model="clubdetails.email_interclub" :label="$t('Email address Interclub')" />
                <v-text-field v-model="clubdetails.email_admin" :label="$t('Email address administration')" />
                <v-text-field v-model="clubdetails.email_finance" :label="$t('Email address finance')" />
                <v-textarea rows="3" v-model="clubdetails.address" :label="$t('Postal address')" />
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card class="elevation-5">
              <v-card-title>
                {{ $t('Bank details') }}
              </v-card-title>
              <v-card-text>
                <v-text-field v-model="clubdetails.bankacount_name" :label="$t('Bank account name')" />
                <v-text-field v-model="clubdetails.bankaccount_iban" :label="$t('Bank account IBAN')" />
                <v-text-field v-model="clubdetails.bankaccount_bic" :label="$t('Bank account BIC')" />
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>
                {{ $t('Playing details') }}
              </v-card-title>
              <v-card-text>
                <v-textarea rows="3" v-model="clubdetails.venue" :label="$t('Club venue')" />
                <h4>{{ $t('Playing hours') }}</h4>
                <v-text-field v-model="clubdetails.openinghours.Monday" :label="$t('Monday')" />                
                <v-text-field v-model="clubdetails.openinghours.Tuesday" :label="$t('Tuesday')" />                
                <v-text-field v-model="clubdetails.openinghours.Wednesday" :label="$t('Wednesday')" />                
                <v-text-field v-model="clubdetails.openinghours.Thursday" :label="$t('Thursday')" />                
                <v-text-field v-model="clubdetails.openinghours.Friday" :label="$t('Friday')" />                
                <v-text-field v-model="clubdetails.openinghours.Saturday" :label="$t('Saturday')" />                
                <v-text-field v-model="clubdetails.openinghours.Sunday" :label="$t('Sunday')" />                
              </v-card-text>
            </v-card>
          </v-col>                    
        </v-row>
        <v-row class="ma-2">
          <v-btn @click="saveClub">{{ $t('Save') }}</v-btn>
          <v-btn @click="cancelClub">{{ $t('Cancel') }}</v-btn>
        </v-row>
      </v-container>
    </div>
    <v-dialog v-model="helpdialog" width="20em">
      <ContentRenderer :value="help">
        <v-card>
          <v-card-title v-html="help[ttitle] ? help[ttitle] : help.title" />
          <v-divider></v-divider>
          <v-card-text class="pa-3 ma-1 markdowncontent" v-html="md(help[tcontent])"> 
          </v-card-text>
        </v-card>
      </ContentRenderer>
    </v-dialog> 
  </v-container>
</template>

<style scoped>
.fieldname {
  color: green;
}
</style>

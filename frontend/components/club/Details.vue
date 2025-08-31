<script setup>
import { ref, computed } from "vue"
import { useI18n } from "vue-i18n"
import { CLUB_STATUS, EMPTY_CLUB } from "@/util/club"
import { useIdtokenStore } from "@/store/idtoken"
import { storeToRefs } from "pinia"

// communication
defineExpose({ setup })
const idstore = useIdtokenStore()
const { token } = storeToRefs(idstore)
const { $backend } = useNuxtApp()
const { t } = useI18n()

// help dialog
// const mdConverter = new showdown.Converter()
// const helptitle = ref("")
// const helpdialog = ref(false)
// const helpcontent = ref("")

//  snackbar and loading widgets
import ProgressLoading from "@/components/ProgressLoading.vue"
import SnackbarMessage from "@/components/SnackbarMessage.vue"
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

// model
const club = ref(EMPTY_CLUB)
const clubmembers = ref([])
const statuscm = ref(CLUB_STATUS.CONSULTING)
const status_consulting = computed(() => statuscm.value == CLUB_STATUS.CONSULTING)
const status_modifying = computed(() => statuscm.value == CLUB_STATUS.MODIFYING)
let copyclub = null

// function md(s) {
//   return mdConverter.makeHtml(s)
// }

function cancelClub() {
  statuscm.value = CLUB_STATUS.CONSULTING
  club.value = copyclub
}

function gotoLogin() {
  console.log("login in details")
}

async function modifyClub() {
  statuscm.value = CLUB_STATUS.MODIFYING
}

async function saveClub() {
  // build a a diff between club and its cooy
  let update = {}
  for (const [key, value] of Object.entries(club.value)) {
    if (value != copyclub[key]) {
      update[key] = value
    }
  }
  showLoading(true)
  try {
    const reply = await $backend("club", "clb_update_club", {
      ...update,
      idclub: club.value.idclub,
      token: token.value,
    })
    statuscm.value = CLUB_STATUS.CONSULTING
    showSnackbar(t("Club saved"))
  } catch (error) {
    if (error.code == 401) gotoLogin()
    showSnackbar(t("Saving club failed"))
  } finally {
    showLoading(false)
  }
}

// async function getContent() {
//   try {
//     const reply = await $backend("filestore", "anon_get_file", {
//       group: "pages",
//       name: `help-club-contact.md`,
//     })
//     metadata.value = useMarkdown(reply.data).metadata
//     helptitle.value = metadata.value["title_" + locale.value]
//     helpcontent.value = mdConverter.makeHtml(metadata.value["content_" + locale.value])
//   } catch (error) {
//     console.log("failed")
//   }
// }

function setup(club_) {
  console.log("setup details", club_)
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  club.value = { ...EMPTY_CLUB, ...club_ }
  console.log("club", club.value)
  copyclub = JSON.parse(JSON.stringify(club_))
  // getContent()
}
</script>

<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <p v-if="!club.idclub">{{ $t("Select a club to view the club details") }}</p>
    <div v-if="club.idclub">
      <v-container v-show="status_consulting">
        <h2>{{ $t("Consulting club details") }}</h2>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>
                {{ $t("Club details") }}
              </v-card-title>
              <v-card-text>
                <div>
                  <span class="fieldname">{{ $t("Long name") }}</span
                  >: {{ club.name_long }}
                </div>
                <div>
                  <span class="fieldname">{{ $t("Short name") }}</span
                  >: {{ club.name_short }}
                </div>
                <div>
                  <span class="fieldname">{{ $t("Federation") }}</span
                  >: {{ club.federation }}
                </div>
                <div>
                  <span class="fieldname">{{ $t("Website") }}</span
                  >: {{ club.website }}
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>{{ $t("Bank details") }}</v-card-title>
              <v-card-text>
                <div>
                  <span class="fieldname">{{ $t("Bank account name") }}</span
                  >: {{ club.bankaccount_name }}
                </div>
                <div>
                  <span class="fieldname">{{ $t("Bank account IBAN") }}</span
                  >: {{ club.bankaccount_iban }}
                </div>
                <div>
                  <span class="fieldname">{{ $t("Bank account BIC") }}</span
                  >: {{ club.bankaccount_bic }}
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title class="mt-2">
                <v-btn
                  icon="mdi-help"
                  color="green"
                  size="small"
                  class="float-right"
                  @click="helpdialog = true"
                />
                <h4>{{ $t("Contact") }}</h4>
              </v-card-title>
              <v-card-text>
                <div>
                  <span class="fieldname">{{ $t("Main email address") }}</span
                  >: {{ club.email_main }}
                </div>
                <div>
                  <span class="fieldname">{{ $t("Email address Interclub") }}</span
                  >: {{ club.email_interclub }}
                </div>
                <div>
                  <span class="fieldname">{{ $t("Email address administration") }}</span
                  >: {{ club.email_admin }}
                </div>
                <div>
                  <span class="fieldname">{{ $t("Email address finance") }}</span
                  >: {{ club.email_finance }}
                </div>
                <div>
                  <span class="fieldname">{{ $t("Postal address") }}</span
                  >:<br />
                  <span v-html="club.address.replaceAll('\n', '<br />')"></span>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>
                {{ $t("Playing details") }}
              </v-card-title>
              <v-card-text>
                <div>
                  <span class="fieldname">{{ $t("Club venue") }}</span
                  >:<br />
                  <span v-html="club.venue.replaceAll('\n', '<br />')"></span>
                </div>
                <h4>{{ $t("Playing hours") }}</h4>
                <div v-for="(h, d) in club.openinghours" :key="d">
                  <div v-show="h.length">
                    <span class="fieldname">{{ $t(d) }}</span
                    >: {{ h }}
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row class="mt-2">
          <v-btn @click="modifyClub">{{ $t("Modify") }}</v-btn>
        </v-row>
      </v-container>
      <v-container v-show="status_modifying">
        <h2>{{ $t("Modify club details") }}</h2>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card class="elevation-5">
              <v-card-title>
                {{ $t("Club details") }}
              </v-card-title>
              <v-card-text>
                <v-text-field v-model="club.name_long" :label="$t('Long name')" />
                <v-text-field v-model="club.name_short" :label="$t('Short name')" />
                <p>{{ $t("Federation") }}: {{ club.federation }}</p>
                <v-text-field v-model="club.website" label="Website" />
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card class="elevation-5">
              <v-card-title>
                {{ $t("Contact") }}
              </v-card-title>
              <v-card-text>
                <v-text-field
                  v-model="club.email_main"
                  :label="$t('Main email address')"
                />
                <v-text-field
                  v-model="club.email_interclub"
                  :label="$t('Email address Interclub')"
                />
                <v-text-field
                  v-model="club.email_admin"
                  :label="$t('Email address administration')"
                />
                <v-text-field
                  v-model="club.email_finance"
                  :label="$t('Email address finance')"
                />
                <v-textarea
                  rows="3"
                  v-model="club.address"
                  :label="$t('Postal address')"
                />
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card class="elevation-5">
              <v-card-title>
                {{ $t("Bank details") }}
              </v-card-title>
              <v-card-text>
                <v-text-field
                  v-model="club.bankaccount_name"
                  :label="$t('Bank account name')"
                />
                <v-text-field
                  v-model="club.bankaccount_iban"
                  :label="$t('Bank account IBAN')"
                />
                <v-text-field
                  v-model="club.bankaccount_bic"
                  :label="$t('Bank account BIC')"
                />
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>
                {{ $t("Playing details") }}
              </v-card-title>
              <v-card-text>
                <v-textarea rows="3" v-model="club.venue" :label="$t('Club venue')" />
                <h4>{{ $t("Playing hours") }}</h4>
                <v-text-field v-model="club.openinghours.Monday" :label="$t('Monday')" />
                <v-text-field
                  v-model="club.openinghours.Tuesday"
                  :label="$t('Tuesday')"
                />
                <v-text-field
                  v-model="club.openinghours.Wednesday"
                  :label="$t('Wednesday')"
                />
                <v-text-field
                  v-model="club.openinghours.Thursday"
                  :label="$t('Thursday')"
                />
                <v-text-field v-model="club.openinghours.Friday" :label="$t('Friday')" />
                <v-text-field
                  v-model="club.openinghours.Saturday"
                  :label="$t('Saturday')"
                />
                <v-text-field v-model="club.openinghours.Sunday" :label="$t('Sunday')" />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row class="ma-2">
          <v-btn @click="saveClub">{{ $t("Save") }}</v-btn>
          <v-btn @click="cancelClub">{{ $t("Cancel") }}</v-btn>
        </v-row>
      </v-container>
    </div>
    <v-dialog v-model="helpdialog" width="20em">
      <v-card>
        <v-card-title v-html="helptitle" />
        <v-divider></v-divider>
        <v-card-text class="pa-3 ma-1 markdowncontent" v-html="helpcontent" />
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.fieldname {
  color: green;
}
</style>

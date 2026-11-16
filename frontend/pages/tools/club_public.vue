<script setup>
import { ref, onMounted } from "vue"
import { useI18n } from "vue-i18n"

import { EMPTY_CLUB } from "@/util/club"

const route = useRoute()
const { locale, t: $t } = useI18n()
const { $backend } = useNuxtApp()
const boardmembers = ref({})
const club = ref({ ...EMPTY_CLUB })
const clubs = ref([])

const idclub = ref(null)

// wating dialog
let dialogcounter = 0
const waitingdialog = ref(false)

// A club's website, as a link only when it is a plain http(s) address. A club
// admin types it, and a javascript: or data: address in an href runs on this
// site when a visitor clicks it, where the member token is kept. An address
// typed without a scheme ("www.club.be") gets https://.
function webLink(url) {
  let text = String(url || "").trim()
  if (!text) return ""
  if (!text.includes(":")) text = "https://" + text
  try {
    const parsed = new URL(text)
    if (parsed.protocol === "http:" || parsed.protocol === "https:") return parsed.href
  } catch (e) {
    // not an address: no link
  }
  return ""
}
function changeDialogCounter(i) {
  dialogcounter += i
  waitingdialog.value = dialogcounter > 0
}

// snackbar
const errortext = ref(null)
const snackbar = ref(null)
function displaySnackbar(text, color) {
  errortext.value = text
  snackbar.value = true
}

async function getClubs() {
  let reply
  changeDialogCounter(1)
  try {
    reply = await $backend("club", "anon_get_clubs", {})
  } catch (error) {
    displaySnackbar($t(error.message))
    return
  } finally {
    changeDialogCounter(-1)
  }
  clubs.value = reply.data
  clubs.value.forEach((p) => {
    p.merged = `${p.idclub}: ${p.name_short} ${p.name_long}`
  })
}

async function getClubDetails() {
  let reply
  club.value = EMPTY_CLUB
  if (idclub.value) {
    changeDialogCounter(1)
    try {
      reply = await $backend("club", "anon_get_club", {
        idclub: idclub.value,
      })
    } catch (error) {
      displaySnackbar(t(t(error.message)))
      return
    } finally {
      changeDialogCounter(-1)
    }
    club.value = reply.data
  }
}

function selectclub() {
  getClubDetails()
}

onMounted(() => {
  let l = route.query.locale
  locale.value = l ? l : "nl"
  getClubs()
})

definePageMeta({
  layout: "nomenu",
})
</script>

<template>
  <v-container>
    <h1>{{ $t("Club details") }}</h1>
    <v-dialog width="10em" v-model="waitingdialog">
      <v-card>
        <v-card-title>{{ $t("Loading...") }}</v-card-title>
        <v-card-text>
          <v-progress-circular indeterminate color="green" />
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-card class="mt-2">
      <v-card-text>
        <p v-if="!club.idclub">{{ $t("Select a club to view the club details") }}</p>
        <VAutocomplete
          v-model="idclub"
          :items="clubs"
          item-title="merged"
          item-value="idclub"
          color="green"
          label="Club"
          clearable
          @update:model-value="selectclub"
        >
        </VAutocomplete>
      </v-card-text>
    </v-card>

    <div v-if="club.idclub" class="mt-3">
      <v-row>
        <v-col cols="12" md="6">
          <h4>{{ $t("Details") }}</h4>
          <div>
            <span class="text-green-darken-2">{{ $t("Long name") }}</span
            >: {{ club.name_long }}
          </div>
          <div>
            <span class="text-green-darken-2">{{ $t("Short name") }}</span
            >: {{ club.name_short }}
          </div>
          <div>
            <span class="text-green-darken-2">{{ $t("Club venue") }}</span
            >:<br />
            <span style="white-space: pre-line">{{ club.venue }}</span>
          </div>
          <h4 class="mt-2">{{ $t("Contact") }}</h4>
          <div>
            <span class="text-green-darken-2">{{ $t("Main email address") }}</span
            >: {{ club.email_main }}
          </div>
          <div>
            <span class="text-green-darken-2">{{ $t("Postal address") }}</span
            >:<br />
            <span style="white-space: pre-line">{{ club.address }}</span>
          </div>
          <div>
            <span class="text-green-darken-2">{{ $t("Website") }}</span
            >:
            <a v-if="webLink(club.website)" :href="webLink(club.website)" target="_blank" rel="noopener">{{
              club.website
            }}</a>
            <span v-else>{{ club.website }}</span>
          </div>
        </v-col>

        <v-col cols="12" sm="6" lg="4">
          <h4>{{ $t("Board members") }}</h4>
          <ul>
            <li v-for="(bm, f) in club.boardmembers" :key="f">
              <span class="text-green-darken-2">{{ $t(f) }}</span
              >: {{ bm.first_name }} {{ bm.last_name }}<br />
              <span v-show="bm.email && bm.email != '#NA'"
                >e-mail: {{ bm.email }}<br
              /></span>
              <span v-show="bm.mobile && bm.mobile != '#NA'"
                >gsm: {{ bm.mobile }}<br
              /></span>
            </li>
          </ul>
        </v-col>
      </v-row>
    </div>
    <VSnackbar v-model="snackbar" timeout="6000">
      {{ errortext }}
      <template v-slot:actions>
        <v-btn
          color="green-lighten-2"
          variant="text"
          @click="snackbar = false"
          icon="mdi-close"
        />
      </template>
    </VSnackbar>
  </v-container>
</template>

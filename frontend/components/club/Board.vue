<script setup>
import { ref, computed } from "vue"
import { useI18n } from "vue-i18n"

import { visibility_items, CLUB_STATUS, EMPTY_BOARD, EMPTY_CLUB } from "@/util/club"
import { useIdtokenStore } from "@/store/idtoken"
import { storeToRefs } from "pinia"

// communication
defineExpose({ setup })
const emit = defineEmits(["updateClub"])
const idstore = useIdtokenStore()
const { token } = storeToRefs(idstore)
const { $backend } = useNuxtApp()
const { t } = useI18n()

//  snackbar and loading widgets
import ProgressLoading from "@/components/ProgressLoading.vue"
import SnackbarMessage from "@/components/SnackbarMessage.vue"
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

// model
const { locale, t: $t } = useI18n()
const router = useRouter()
const boardmembers = ref(EMPTY_BOARD)
const club = ref(EMPTY_CLUB)
const clubmembers = ref([])
const statuscm = ref(CLUB_STATUS.CONSULTING)
const status_consulting = computed(() => statuscm.value == CLUB_STATUS.CONSULTING)
const status_modifying = computed(() => statuscm.value == CLUB_STATUS.MODIFYING)
const t_vis_items = computed(() =>
  visibility_items.map((x) => ({
    title: $t(x.title),
    value: x.value,
  }))
)
let copyclub = null

function cancelClub() {
  statuscm.value = CLUB_STATUS.CONSULTING
}

function gotoLogin() {
  console.log("login in board")
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
  showLoading = true
  try {
    const reply = await $backend("club", "clb_update_club", {
      ...update,
      idclub: club.value.idclub,
      token: token.value,
    })
    statuscm.value = CLUB_STATUS.CONSULTING
    showSnackbar($t("Club saved"))
  } catch (error) {
    if (error.code == 401) gotoLogin()
    showSnackbar($t(error.message))
    return
  } finally {
    showLoading = false
  }
  emit("updateClub")
}

function updateboard(f) {
  const bm = boardmembers.value[f]
  if (bm.idnumber) {
    let cm = clubmembers.value.find((x) => x.idnumber == bm.idnumber)
    bm.first_name = cm.first_name
    bm.last_name = cm.last_name
    bm.email = cm.email
    bm.mobile = cm.mobile
    bm.email_visibility = "CLUB"
    bm.mobile_visibility = "CLUB"
    club.value.boardmembers[f] = bm
  } else {
    bm.first_name = null
    bm.last_name = null
    bm.email = null
    bm.mobile = null
    bm.email_visibility = null
    bm.mobile_visibility = null
    delete club.value.boardmembers[f]
  }
}

function setup(club_, clubmembers_) {
  console.log("setup Board", club_, clubmembers_)
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  club.value = { ...EMPTY_CLUB, ...club_ }
  clubmembers.value = clubmembers_
  copyclub = JSON.parse(JSON.stringify(club.value))
  boardmembers.value = { ...EMPTY_BOARD, ...club.value.boardmembers }
}
</script>

<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <p v-if="!club.idclub">{{ $t("Select a club to view the club details") }}</p>
    <div v-if="club.idclub">
      <v-container v-if="status_consulting">
        <h2>{{ $t("Consulting board members") }}</h2>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3" v-for="(bm, f) in boardmembers" :key="f">
            <v-card class="elevation-5">
              <v-card-title class="text-green">
                {{ $t(f) }}
              </v-card-title>
              <v-card-text>
                {{ $t("Name") }}: {{ bm.first_name }} {{ bm.last_name }}<br />
                {{ $t("Email") }}: {{ bm.email }}<br />
                {{ $t("Mobile") }}: {{ bm.mobile }}
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row class="mt-2">
          <v-btn @click="modifyClub">{{ $t("Modify") }}</v-btn>
        </v-row>
      </v-container>
      <v-container v-if="status_modifying">
        <h2>{{ $t("Modify board members") }}</h2>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3" v-for="(bm, f) in boardmembers" :key="f">
            <v-card class="elevation-5">
              <v-card-title class="text-green">
                {{ $t(f) }}
              </v-card-title>
              <v-card-text>
                <v-autocomplete
                  v-model="boardmembers[f].idnumber"
                  :items="clubmembers"
                  item-title="merged"
                  item-value="idnumber"
                  color="green"
                  clearable
                  @update:model-value="updateboard(f)"
                >
                </v-autocomplete>
                <v-text-field
                  label="Email"
                  v-model="boardmembers[f].email"
                ></v-text-field>
                <v-select
                  v-model="boardmembers[f].email_visibility"
                  :items="t_vis_items"
                  color="green"
                  label="Email visibility"
                />
                <v-text-field label="GSM" v-model="boardmembers[f].mobile"></v-text-field>
                <v-select
                  v-model="boardmembers[f].mobile_visibility"
                  :items="t_vis_items"
                  color="green"
                  label="Mobile visibility"
                />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row class="ma-2">
          <v-btn @click="saveClub">{{ $t("Save club") }}</v-btn>
          <v-btn @click="cancelClub">{{ $t("Cancel") }}</v-btn>
        </v-row>
      </v-container>
    </div>
  </v-container>
</template>

<style scoped>
.fieldname {
  color: green;
}

.v-card__text,
.v-card__title {
  word-break: normal;
  /* maybe !important  */
}
</style>

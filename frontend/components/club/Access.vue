<script setup>
import { ref, computed, nextTick } from "vue"
import { useI18n } from "vue-i18n"

import { visibility_items, CLUB_STATUS, EMPTY_CLUB } from "@/util/club"
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
const router = useRouter()
const club = ref(EMPTY_CLUB)
const clubadmin = ref({})
const clubmembers = ref([])
let copyclub = null
const interclubadmin = ref({})
const interclubcaptain = ref({})
const newclubadmin = ref(null)
const newinterclubadmin = ref(null)
const newinterclubcaptain = ref(null)
const statuscm = ref(CLUB_STATUS.CONSULTING)
const status_consulting = computed(() => statuscm.value == CLUB_STATUS.CONSULTING)
const status_modifying = computed(() => statuscm.value == CLUB_STATUS.MODIFYING)
const t_vis_items = computed(() =>
  visibility_items.map((x) => ({
    title: t(x.title),
    value: x.value,
  }))
)
let clubadminl, interclubadminl

function addClubAdmin() {
  const cm = clubmembers.value.find((m) => m.idnumber == newclubadmin.value)
  clubadmin.value[newclubadmin.value] = cm.merged
  nextTick(() => (newclubadmin.value = null))
}

function addInterclubAdmin() {
  interclubadmin.value[newinterclubadmin.value] = clubmembers.value.find(
    (m) => m.idnumber == newinterclubadmin.value
  ).merged
  nextTick(() => (newinterclubadmin.value = 0))
}

function cancelAccess() {
  statuscm.value = CLUB_STATUS.CONSULTING
  emit("updateClub")
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

function gotoLogin() {
  console.log("login in access")
}

async function modifyAccess() {
  statuscm.value = CLUB_STATUS.MODIFYING
}

function readClubMembers() {
  console.log("reading club members", clubadminl)
  clubadmin.value = Object.fromEntries(
    clubadminl.map((x) => {
      const cm = clubmembers.value.find((m) => m.idnumber == x)
      if (!cm) {
        console.log("Did not find", x)
        return []
      } else {
        cm.merged = cm ? `${x} ${cm.first_name} ${cm.last_name}` : ""
        return [x, cm.merged]
      }
    })
  )
  interclubadmin.value = Object.fromEntries(
    interclubadminl.map((x) => {
      const cm = clubmembers.value.find((m) => m.idnumber == x)
      if (!cm) {
        console.log("Did not find", x)
        return []
      } else {
        cm.merged = cm ? `${x} ${cm.first_name} ${cm.last_name}` : ""
        return [x, cm.merged]
      }
    })
  )
}

async function saveAccess() {
  // build a a diff between club and its cooy
  console.log("saving")
  club.value.clubroles.forEach((c) => {
    if (c.nature == "ClubAdmin") c.memberlist = Object.keys(clubadmin.value)
    if (c.nature == "InterclubAdmin") c.memberlist = Object.keys(interclubadmin.value)
  })
  showLoading = true
  try {
    const reply = await $backend("club", "clb_update_club", {
      clubroles: club.value.clubroles,
      idclub: club.value.idclub,
      token: token.value,
    })
    statuscm.value = CLUB_STATUS.CONSULTING
    showSnackbar(t("Club saved"))
    emit("updateClub")
  } catch (error) {
    if (error.code == 401) gotoLogin()
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading = false
  }
}

function setup(club_, clubmembers_) {
  console.log("setup Board", club_, clubmembers_)
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  club.value = { ...EMPTY_CLUB, ...club_ }
  clubmembers.value = clubmembers_
  copyclub = JSON.parse(JSON.stringify(club.value))
  club.value.clubroles.forEach((c) => {
    console.log("loop c", c.nature, c.memberlist)
    if (c.nature == "ClubAdmin") clubadminl = c.memberlist
    if (c.nature == "InterclubAdmin") interclubadminl = c.memberlist
  })
  console.log("clubadmin", clubadmin.value)
  readClubMembers()
}
</script>

<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <p v-if="!club.idclub">{{ $t("Select a club to view the access rights") }}</p>
    <div v-if="club.idclub" class="markdowncontent">
      <v-container v-show="status_consulting">
        <h2>{{ $t("Consulting access rights") }}</h2>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>{{ $t("Club administrators") }}</v-card-title>
              <v-card-text>
                {{ $t("The club administrators have write access to the Club Manager") }}
                <ul>
                  <li v-for="(m, ix) in clubadmin" :key="ix">{{ m }}</li>
                </ul>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>{{ $t("Interclub Administrators") }}</v-card-title>
              <v-card-text>
                {{
                  $t(
                    "The interclub administrators have write access to the Interclub Manager"
                  )
                }}
                <ul>
                  <li v-for="(m, ix) in interclubadmin" :key="ix">{{ m }}</li>
                </ul>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row class="ma-2">
          <v-btn @click="modifyAccess">{{ $t("Modify") }}</v-btn>
        </v-row>
      </v-container>

      <v-container v-show="status_modifying">
        <h2>{{ $t("Modify access rights") }}</h2>
        <v-row>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>{{ $t("Club administrators") }}</v-card-title>
              <v-card-text>
                <ul>
                  <li v-for="(m, ix) in clubadmin" :key="m">
                    {{ m }} &nbsp;
                    <v-icon @click="deleteClubAdmin(ix)">mdi-delete</v-icon>
                  </li>
                </ul>
                <v-autocomplete
                  v-model="newclubadmin"
                  :items="clubmembers || []"
                  @update:model-value="addClubAdmin"
                  label="Add Member"
                  class="memberselect"
                  item-title="merged"
                  item-value="idnumber"
                >
                </v-autocomplete>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" xl="3">
            <v-card>
              <v-card-title>{{ $t("Interclub Administrators") }}</v-card-title>
              <v-card-text>
                <ul>
                  <li v-for="(m, ix) in interclubadmin" :key="m">
                    {{ m }} &nbsp;
                    <v-icon @click="deleteInterclubAdmin(ix)">mdi-delete</v-icon>
                  </li>
                </ul>
                <v-autocomplete
                  v-model="newinterclubadmin"
                  :items="clubmembers || []"
                  @update:model-value="addInterclubAdmin"
                  label="Add Member"
                  class="memberselect"
                  item-title="merged"
                  item-value="idnumber"
                >
                </v-autocomplete>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row class="ma-2">
          <v-btn @click="saveAccess">{{ $t("Save") }}</v-btn>
          <v-btn @click="cancelAccess">{{ $t("Cancel") }}</v-btn>
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

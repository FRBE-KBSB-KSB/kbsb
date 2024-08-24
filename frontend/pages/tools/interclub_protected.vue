<script setup>
import { ref, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import Enrollment from "@/components/interclubs/Enrollment.vue";
// import Results from '@/components/interclubs/Results.vue'
// import Planning from '@/components/interclubs/Planning.vue'
// import Playerlist from '@/components/interclubs/Playerlist.vue'
import Venue from "@/components/interclubs/Venue.vue";
import { parse } from "yaml";
import { useIdtokenStore } from "@/store/idtoken";
import { storeToRefs } from "pinia";

// communication
const router = useRouter();
const route = useRoute();
const waitingdialog = ref(false);
let dialogcounter = 0;
const errortext = ref(null);
const snackbar = ref(null);

// locale
const { locale, t } = useI18n();

// API backend
const { $backend } = useNuxtApp();
const idstore = useIdtokenStore();
const { token: idtoken } = storeToRefs(idstore);

// data model
const tab = ref(null);
const refenrollment = ref(null);
const refplanning = ref(null);
const refplayerlist = ref(null);
const refresults = ref(null);
const refvenues = ref(null);
const icdata = ref({});
const clubs = ref([]);
const icclub = ref({}); // the icclub data
const idclub = ref(null);
const ic_rounds = ref([]);
const round = ref("1");

// methods alphabetically

function changeDialogCounter(i) {
  dialogcounter += i;
  waitingdialog.value = dialogcounter > 0;
}

function changeTab() {
  console.log("changeTab", tab.value);
  switch (tab.value) {
    case "enrollment":
      refenrollment.value.setup(icclub.value, icdata.value);
      break;
    case "planning":
      refplanning.value.setup(icclub.value, round.value);
      break;
    case "playerlist":
      refplayerlist.value.setup(icclub.value);
      break;
    case "results":
      refresults.value.setup(icclub.value, round.value);
      break;
    case "venues":
      refvenues.value.setup(icclub.value, icdata.value);
      break;
  }
}

function checkAuth() {
  if (!idtoken.value) {
    gotoLogin();
  }
}

function displaySnackbar(text, color) {
  errortext.value = text;
  snackbar.value = true;
}

async function getClubs() {
  let reply;
  changeDialogCounter(1);
  try {
    reply = await $backend("club", "anon_get_clubs", {});
  } catch (error) {
    if (error.code == 401) gotoLogin();
    displaySnackbar(t(error.message));
    return;
  } finally {
    changeDialogCounter(-1);
  }
  clubs.value = reply.data;
  clubs.value.forEach((p) => {
    p.merged = `${p.idclub}: ${p.name_short} ${p.name_long}`;
  });
}

async function getClubDetails() {
  let reply;
  icclub.value = { idclub: idclub.value };
  changeDialogCounter(1);
  try {
    reply = await $backend("interclub", "clb_getICclub", {
      idclub: idclub.value,
      token: idtoken.value,
    });
    icclub.value = { idclub: idclub.value, ...(reply.data || {}) };
  } catch (error) {
    console.log("did not find clubdetails", icclub.value);
    if (error.code == 401) gotoLogin();
    displaySnackbar(t(error.message));
    return;
  } finally {
    changeDialogCounter(-1);
    changeTab();
  }
}

async function gotoLogin() {
  await router.push("/tools/oldlogin?url=__tools__interclub_protected");
}

async function parseYaml(group, name) {
  try {
    const yamlcontent = await readBucket(group, name);
    if (!yamlcontent) {
      return null;
    }
    return parse(yamlcontent);
  } catch (error) {
    console.error("cannot parse yaml", yamlcontent);
  }
}

async function processICdata() {
  icdata.value = await parseYaml("data", "ic2425.yml");
  ic_rounds.value = Object.keys(icdata.value.rounds).map((x) => {
    return { value: x, title: `R${x}: ${icdata.value.rounds[x]}` };
  });
}

async function readBucket(group, name) {
  try {
    const reply = await $backend("filestore", "anon_get_file", {
      group,
      name,
    });
    return reply.data;
  } catch (error) {
    console.error("failed to fetch file from bucket");
    return null;
  }
}

function selectClub() {
  console.log("selected", idclub.value);
  getClubDetails();
}

// startup

onMounted(async () => {
  let l = route.query.locale;
  console.log("query locale", l);
  locale.value = l ? l : "nl";
  checkAuth();
  await processICdata();
  getClubs();
  tab.value = "enrollment";
  changeTab();
});

definePageMeta({
  layout: "nomenu",
});
</script>

<template>
  <VContainer>
    <h1>Interclubs Manager 2024-25</h1>
    <v-dialog width="10em" v-model="waitingdialog">
      <v-card>
        <v-card-title>{{ t("Loading...") }}</v-card-title>
        <v-card-text>
          <v-progress-circular indeterminate color="green" />
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-card>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6">
            <VAutocomplete
              v-model="idclub"
              :items="clubs"
              item-title="merged"
              item-value="idclub"
              color="green"
              label="Club"
              clearable
              @update:model-value="selectClub"
            >
            </VAutocomplete>
          </v-col>
          <v-col cols="12" sm="6">
            <VSelect
              v-model="round"
              :items="ic_rounds"
              :label="t('Round')"
              @update:model-value="changeTab"
            >
            </VSelect>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    <h3 class="my-2">{{ t("Selected club") }}: {{ icclub.idclub }} {{ icclub.name }}</h3>
    <div class="elevation-2">
      <v-tabs v-model="tab" color="green" @update:modelValue="changeTab">
        <v-tab value="enrollment">{{ t("icn.enr") }}</v-tab>
        <!-- <v-tab value="results">{{ t('Results') }}</v-tab>
        <v-tab value="planning">{{ t('Planning') }}</v-tab> -->
        <v-tab value="venues">{{ t("icn.ven_1") }}</v-tab>
        <!-- <v-tab value="playerlist">{{ t('Player list') }}</v-tab> -->
      </v-tabs>
      <v-window v-model="tab" @update:modelValue="changeTab">
        <v-window-item :eager="true" value="enrollment">
          <Enrollment
            ref="refenrollment"
            @snackbar="displaySnackbar"
            @changeDialogCounter="changeDialogCounter"
          />
        </v-window-item>
        <v-window-item :eager="true" value="results">
          <Results
            ref="refresults"
            @snackbar="displaySnackbar"
            @changeDialogCounter="changeDialogCounter"
          />
        </v-window-item>
        <v-window-item :eager="true" value="planning">
          <Planning
            ref="refplanning"
            @snackbar="displaySnackbar"
            @changeDialogCounter="changeDialogCounter"
          />
        </v-window-item>
        <v-window-item :eager="true" value="venues">
          <Venue
            ref="refvenues"
            @snackbar="displaySnackbar"
            @changeDialogCounter="changeDialogCounter"
          />
        </v-window-item>
        <v-window-item :eager="true" value="playerlist">
          <Playerlist ref="refplayerlist" />
        </v-window-item>
      </v-window>
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
  </VContainer>
</template>

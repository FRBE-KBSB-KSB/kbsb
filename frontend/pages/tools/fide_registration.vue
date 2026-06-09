<script setup>
import { ref, onMounted, computed, watch } from "vue";
import { useRoute } from "vue-router";

// communication
const { $backend } = useNuxtApp()
const route = useRoute()

// State
const lang = ref(route.query.locale || "en");
const waitingdialog = ref(false);
const errorText = ref("");

// Lookups and Translations
const lookups = ref({
  yes_no: [],
  age_limit_options: [],
  inc_delay_options: [],
  tiebreak_options: [],
  software_options: [],
  tournament_report_options: [],
  kind_of_arbiters_options: [],
  tournament_system_options: [],
  fide_people: {},
  fide_names: [],
  time_control_types: [],
  time_control_desc: {}
});
const translations = ref(null);

// Form data
const form = ref({
  invoice_email: "",
  invoice_clubnr: "",
  fide_laws_followed: "Yes",
  national_championship_143a: "",
  on_fide_calendar: "",
  tournament_report: "",
  tournament_type: "Over the Board",
  event_name: "",
  city: "",
  country: "",
  expected_players: "",
  tournament_system: "",
  rounds_reported: "",
  multiple_round_days: "0",
  female_only: "",
  start_date: "",
  end_date: "",
  title_norms: "",
  gm_wgm_norms: "",
  chief_arbiter_name: "", chief_arbiter_fide_id: "",
  dep_chief_arbiter1_name: "", dep_chief_arbiter1_fide_id: "",
  dep_chief_arbiter2_name: "", dep_chief_arbiter2_fide_id: "",
  kind_of_arbiters: "",
  arbiter1_name: "", arbiter1_fide_id: "",
  arbiter2_name: "", arbiter2_fide_id: "",
  arbiter3_name: "", arbiter3_fide_id: "",
  arbiter4_name: "", arbiter4_fide_id: "",
  chief_organizer_name: "", chief_organizer_fide_id: "",
  organizer1_name: "", organizer1_fide_id: "",
  organizer2_name: "", organizer2_fide_id: "",
  organizer3_name: "", organizer3_fide_id: "",
  time_control_code: "", time_control_desc: "", timectl_other_desc: "",
  timectl1_moves: "", timectl1_minutes: "", timectl1_inc_type: "", timectl1_inc_seconds: "",
  timectl2_moves: "", timectl2_minutes: "", timectl2_inc_type: "", timectl2_inc_seconds: "",
  timectl_final_minutes: "", timectl_final_inc_type: "", timectl_final_inc_seconds: "",
  max_rating: "",
  age_limit: "", age_limit_value: "",
  all_digital_clocks: "",
  internet_tx: "", internet_tx_boards: "",
  tiebreak_method: "", tiebreak_other: "",
  software: "", software_other: "", software_version: "",
  pgn_provided: "No",
  contact_email: "", homepage: "", prize_fund: "", remarks: ""
});

// Create round fields
for (let i = 1; i <= 100; i++) {
  form.value[`round${i}_date`] = "";
  form.value[`round${i}_report`] = "";
}

// Translations helpers
const tUI = (key) => translations.value?.[lang.value]?.ui?.[key] || key;
const tField = (key) => translations.value?.[lang.value]?.fields?.[key] || key;
const tCat = (key) => translations.value?.[lang.value]?.categories?.[key] || key;
const tMsg = (key) => translations.value?.[lang.value]?.messages?.[key] || key;

const tOptYesNo = (val) => translations.value?.[lang.value]?.options?.yes_no?.[val] || val;
const tOptAge = (val) => translations.value?.[lang.value]?.options?.age_limit?.[val] || val;
const tOptInc = (val) => translations.value?.[lang.value]?.options?.inc_delay?.[val] || val;

// Computed Properties
const isLongTournament = computed(() => form.value.tournament_report === 'New long tournament');
const roundsCount = computed(() => parseInt(form.value.rounds_reported) || 0);

const timeControlDescOptions = computed(() => {
  if (!form.value.time_control_code) return [];
  return lookups.value.time_control_desc[form.value.time_control_code] || [];
});

// Helper functions for round dates and FIDE period logic
function getFidePeriod(dateString) {
  if (!dateString) return null;
  const parts = dateString.split('-');
  if (parts.length !== 3) return null;
  const year = parseInt(parts[0], 10);
  const month = parseInt(parts[1], 10);
  const day = parseInt(parts[2], 10);
  if (isNaN(year) || isNaN(month) || isNaN(day)) return null;

  const lastDay = new Date(year, month, 0).getDate();
  let periodYear = year;
  let periodMonth = month;

  if (day >= lastDay - 1) {
    periodMonth += 1;
    if (periodMonth > 12) {
      periodMonth = 1;
      periodYear += 1;
    }
  }
  return { year: periodYear, month: periodMonth, key: `${periodYear}-${periodMonth}` };
}

function getRoundDateError(index) {
  if (index <= 1) return "";
  const currentDate = form.value[`round${index}_date`];
  if (!currentDate) return "";
  
  // Find the previous populated date
  let prevDate = "";
  let prevIdx = 0;
  for (let i = index - 1; i >= 1; i--) {
    if (form.value[`round${i}_date`]) {
      prevDate = form.value[`round${i}_date`];
      prevIdx = i;
      break;
    }
  }
  
  if (prevDate && currentDate < prevDate) {
    return tMsg('round_dates_order_error')
      .replace('{num}', index)
      .replace('{prev_num}', prevIdx);
  }
  return "";
}

function recalculateReportNumbers() {
  if (!isLongTournament.value) return;

  const count = roundsCount.value;
  const roundsData = [];

  for (let i = 1; i <= count; i++) {
    const dateVal = form.value[`round${i}_date`];
    if (dateVal) {
      const period = getFidePeriod(dateVal);
      roundsData.push({
        index: i,
        dateVal: dateVal,
        period: period
      });
    }
  }

  // Get unique FIDE periods
  const uniquePeriods = [];
  roundsData.forEach(item => {
    if (item.period) {
      const exists = uniquePeriods.some(p => p.key === item.period.key);
      if (!exists) {
        uniquePeriods.push(item.period);
      }
    }
  });

  // Sort periods chronologically
  uniquePeriods.sort((a, b) => {
    if (a.year !== b.year) return a.year - b.year;
    return a.month - b.month;
  });

  // Assign report numbers
  for (let i = 1; i <= 100; i++) {
    if (i <= count) {
      const dateVal = form.value[`round${i}_date`];
      if (dateVal) {
        const item = roundsData.find(r => r.index === i);
        if (item && item.period) {
          const idx = uniquePeriods.findIndex(p => p.key === item.period.key);
          form.value[`round${i}_report`] = String(idx + 1);
        } else {
          form.value[`round${i}_report`] = "";
        }
      } else {
        form.value[`round${i}_report`] = "";
      }
    } else {
      form.value[`round${i}_report`] = "";
    }
  }

  // Recalculate start and end dates
  const activeDates = roundsData.map(r => r.dateVal).filter(Boolean).sort();
  if (activeDates.length > 0) {
    form.value.start_date = activeDates[0];
    form.value.end_date = activeDates[activeDates.length - 1];
  } else {
    form.value.start_date = "";
    form.value.end_date = "";
  }

  // Recalculate multiple round days
  const reportValues = roundsData
    .map(r => form.value[`round${r.index}_report`])
    .filter(Boolean);
  if (reportValues.length > 0) {
    const uniqueReports = new Set(reportValues);
    form.value.multiple_round_days = String(reportValues.length - uniqueReports.size);
  } else {
    form.value.multiple_round_days = "0";
  }
}

// Watchers
watch(() => form.value.time_control_code, () => {
  form.value.time_control_desc = "";
});

watch(isLongTournament, (isLong) => {
  if (!isLong) {
    form.value.start_date = "";
    form.value.end_date = "";
    form.value.multiple_round_days = "0";
    for (let i = 1; i <= 100; i++) {
      form.value[`round${i}_date`] = "";
      form.value[`round${i}_report`] = "";
    }
  } else {
    recalculateReportNumbers();
  }
});

watch(roundsCount, () => {
  recalculateReportNumbers();
});

// Watch active round date fields reactively
watch(
  () => {
    const count = roundsCount.value;
    const dates = [];
    for (let i = 1; i <= count; i++) {
      dates.push(form.value[`round${i}_date`]);
    }
    return dates;
  },
  () => {
    recalculateReportNumbers();
  },
  { deep: true }
);

// Arbiter FIDE lookup
function handleArbiterChange(nameField, idField) {
  const name = form.value[nameField];
  const info = lookups.value.fide_people[name];
  if (info) {
    form.value[idField] = info.id || "";
    if (info.license && info.license.toLowerCase() === 'no license') {
      const ok = confirm(name + " " + tMsg('no_license_confirm'));
      if (!ok) {
        form.value[nameField] = "";
        form.value[idField] = "";
      }
    }
  }
}

// data fetching
async function loadFormData() {
  try {
    const reply = await $backend("fide", "formdata")
    console.log("reply", reply)
    translations.value = reply.data.translations;
    lookups.value = reply.data.lookups;
  } catch (error) {
    console.error(error);
    errorText.value = "Failed to load form data from backend.";
  }
}

async function submitForm() {
  waitingdialog.value = true;
  errorText.value = "";
  try {
    const response = await $backend("fide", "generate", {
      locale: lang.value,
      formdata: form.value,
    })
    console.log("reponse on generate", response)
    let filename = "Tournament_Registration.xlsx";
    const disposition = response.headers.get("content-disposition");
    if (disposition && disposition.indexOf("filename=") !== -1) {
      const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
      if (matches != null && matches[1]) {
        filename = matches[1].replace(/['"]/g, "");
      }
    }
    const blob = new Blob([response.data], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    });
    const downloadUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    urlCreator.revokeObjectURL(downloadUrl);
  } catch (error) {
    console.error(error);
    errorText.value = "Error submitting form";
  } finally {
    waitingdialog.value = false;
  }
}

// Theme logic
const isDark = ref(false);
function toggleTheme() {
  isDark.value = !isDark.value;
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light');
  try { window.localStorage.setItem('fide_theme', isDark.value ? 'dark' : 'light'); } catch (e) {}
}

onMounted(() => {
  loadFormData();
  try {
    const stored = window.localStorage.getItem('fide_theme');
    if (stored === 'dark') {
      isDark.value = true;
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  } catch (e) {}
});

definePageMeta({
  layout: "nomenu",
});
</script>

<template>
  <div v-if="!translations" class="form-shell" style="text-align: center; padding: 3rem;">
    <div v-if="errorText" class="error">{{ errorText }}</div>
    <div v-else>Loading...</div>
  </div>
  <div v-else class="form-shell">
    <div class="shell-header">
      <h1>{{ tUI('title') }}</h1>
      <div class="header-controls">
        <div class="lang-selector">
          <a href="#" @click.prevent="lang = 'en'" :class="['lang-btn', { active: lang === 'en' }]">EN</a>
          <a href="#" @click.prevent="lang = 'nl'" :class="['lang-btn', { active: lang === 'nl' }]">NL</a>
          <a href="#" @click.prevent="lang = 'fr'" :class="['lang-btn', { active: lang === 'fr' }]">FR</a>
        </div>
        <button type="button" @click="toggleTheme" class="theme-toggle" aria-label="Toggle dark mode">
          <span class="icon" aria-hidden="true">{{ isDark ? '☀️' : '🌙' }}</span>
          <span class="label">{{ isDark ? tUI('light_mode') : tUI('dark_mode') }}</span>
        </button>
      </div>
    </div>

    <p class="note note--light" v-html="tUI('mandatory_note')"></p>
    <p class="note note--dark" v-html="tUI('mandatory_note') + ' ' + tUI('dark_mode_note')"></p>
    
    <div v-if="errorText" class="error">{{ errorText }}</div>
    <div v-if="waitingdialog" class="warning">Processing...</div>

    <form @submit.prevent="submitForm">
      <label>
        <span class="required-label">{{ tField('invoice_email') }}</span>
        <input type="email" v-model="form.invoice_email" required>
      </label>
      <label>
        <span class="required-label">{{ tField('invoice_clubnr') }}</span>
        <input type="text" v-model="form.invoice_clubnr" required>
      </label>

      <div class="group-title">{{ tCat('tournament_info') }}</div>
      <p class="note" style="margin-top: 0.5rem; margin-bottom: 1rem; font-style: italic;">{{ tUI('fide_laws_note') }}</p>

      <label>
        <span class="required-label">{{ tField('national_championship_143a') }}</span>
        <select v-model="form.national_championship_143a" required>
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="opt in lookups.yes_no" :key="opt" :value="opt">{{ tOptYesNo(opt) }}</option>
        </select>
      </label>
      <label>
        <span class="required-label">{{ tField('on_fide_calendar') }}</span>
        <select v-model="form.on_fide_calendar" required>
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="opt in lookups.yes_no" :key="opt" :value="opt">{{ tOptYesNo(opt) }}</option>
        </select>
      </label>
      <label>
        <span class="required-label">{{ tField('tournament_report') }}</span>
        <select v-model="form.tournament_report" required>
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="opt in lookups.tournament_report_options" :key="opt" :value="opt">{{ opt }}</option>
        </select>
      </label>
      <label>
        <span class="required-label">{{ tField('tournament_type') }}</span>
        <select v-model="form.tournament_type" required>
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option value="Hybrid">Hybrid</option>
          <option value="Over the Board">Over the Board</option>
        </select>
      </label>
      <label>
        <span class="required-label">{{ tField('tournament_system') }}</span>
        <select v-model="form.tournament_system" required>
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="opt in lookups.tournament_system_options" :key="opt" :value="opt">{{ opt }}</option>
        </select>
      </label>
      <label>
        <span class="required-label">{{ tField('event_name') }}</span>
        <input type="text" v-model="form.event_name" pattern="[A-Za-z0-9 ]+" title="Only letters A-Z, numbers and spaces are allowed." required>
      </label>
      <label>
        <span class="required-label">{{ tField('city') }}</span>
        <input type="text" v-model="form.city" required>
      </label>
      <label>
        <span class="required-label">{{ tField('country') }}</span>
        <input type="text" v-model="form.country" required>
      </label>
      <label>
        <span class="required-label">{{ tField('expected_players') }}</span>
        <input type="number" v-model="form.expected_players" min="1" max="2500" required>
      </label>
      <label>
        <span class="required-label">{{ tField('rounds_reported') }}</span>
        <input type="number" v-model="form.rounds_reported" min="0" max="100" required>
      </label>
      
      <label v-if="!isLongTournament">
        <span class="required-label">{{ tField('multiple_round_days') }}</span>
        <input type="number" v-model="form.multiple_round_days" min="0" max="100" required>
      </label>

      <div v-if="isLongTournament" id="long-tournament-block">
        <div class="group-title">{{ tCat('long_tournament_rounds') }}</div>
        <div id="rounds-container">
          <div class="round-row active" v-for="i in roundsCount" :key="i">
            <label>
              <span class="required-label">{{ tField('round_date').replace('{num}', i) }}</span>
              <input type="date" v-model="form[`round${i}_date`]" required>
              <div v-if="getRoundDateError(i)" class="error-msg" style="color: var(--error); font-size: 0.85rem; margin-top: 0.25rem; font-weight: 500;">
                {{ getRoundDateError(i) }}
              </div>
            </label>
            <label>
              <span class="required-label">{{ tField('round_report').replace('{num}', i) }}</span>
              <input type="number" v-model="form[`round${i}_report`]" min="1" required readonly>
            </label>
          </div>
        </div>
        <div style="margin-top: 1rem; padding-top: 0.5rem; border-top: 1px solid var(--border); font-weight: 500; font-size: 0.95rem; color: var(--accent);">
          {{ tField('multiple_round_days') }}: {{ form.multiple_round_days }}
        </div>
      </div>

      <label>
        <span class="required-label">{{ tField('female_only') }}</span>
        <select v-model="form.female_only" required>
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="opt in lookups.yes_no" :key="opt" :value="opt">{{ tOptYesNo(opt) }}</option>
        </select>
      </label>
      <label v-if="!isLongTournament">
        <span class="required-label">{{ tField('start_date') }}</span>
        <input type="date" v-model="form.start_date" required>
      </label>
      <label v-if="!isLongTournament">
        <span class="required-label">{{ tField('end_date') }}</span>
        <input type="date" v-model="form.end_date" required>
      </label>
      <label>
        <span class="required-label">{{ tField('title_norms') }}</span>
        <select v-model="form.title_norms" required>
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="opt in lookups.yes_no" :key="opt" :value="opt">{{ tOptYesNo(opt) }}</option>
        </select>
      </label>
      <label>
        <span class="required-label">{{ tField('gm_wgm_norms') }}</span>
        <select v-model="form.gm_wgm_norms" required>
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="opt in lookups.yes_no" :key="opt" :value="opt">{{ tOptYesNo(opt) }}</option>
        </select>
      </label>

      <div class="group-title">{{ tCat('arbiters') }}</div>

      <label><span class="required-label">{{ tField('chief_arbiter_name') }}</span>
        <input type="text" v-model="form.chief_arbiter_name" list="fideNames" @change="handleArbiterChange('chief_arbiter_name', 'chief_arbiter_fide_id')" required>
      </label>
      <label><span class="required-label">{{ tField('chief_arbiter_fide_id') }}</span><input type="text" v-model="form.chief_arbiter_fide_id" required></label>
      
      <label><span>{{ tField('dep_chief_arbiter1_name') }}</span>
        <input type="text" v-model="form.dep_chief_arbiter1_name" list="fideNames" @change="handleArbiterChange('dep_chief_arbiter1_name', 'dep_chief_arbiter1_fide_id')">
      </label>
      <label><span>{{ tField('dep_chief_arbiter1_fide_id') }}</span><input type="text" v-model="form.dep_chief_arbiter1_fide_id"></label>
      
      <label><span>{{ tField('dep_chief_arbiter2_name') }}</span>
        <input type="text" v-model="form.dep_chief_arbiter2_name" list="fideNames" @change="handleArbiterChange('dep_chief_arbiter2_name', 'dep_chief_arbiter2_fide_id')">
      </label>
      <label><span>{{ tField('dep_chief_arbiter2_fide_id') }}</span><input type="text" v-model="form.dep_chief_arbiter2_fide_id"></label>
      
      <label>
        <span class="required-label">{{ tField('kind_of_arbiters') }}</span>
        <select v-model="form.kind_of_arbiters" required>
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="opt in lookups.kind_of_arbiters_options" :key="opt" :value="opt">{{ opt }}</option>
        </select>
      </label>
      
      <label><span>{{ tField('arbiter1_name') }}</span><input type="text" v-model="form.arbiter1_name" list="fideNames" @change="handleArbiterChange('arbiter1_name', 'arbiter1_fide_id')"></label>
      <label><span>{{ tField('arbiter1_fide_id') }}</span><input type="text" v-model="form.arbiter1_fide_id"></label>
      <label><span>{{ tField('arbiter2_name') }}</span><input type="text" v-model="form.arbiter2_name" list="fideNames" @change="handleArbiterChange('arbiter2_name', 'arbiter2_fide_id')"></label>
      <label><span>{{ tField('arbiter2_fide_id') }}</span><input type="text" v-model="form.arbiter2_fide_id"></label>
      <label><span>{{ tField('arbiter3_name') }}</span><input type="text" v-model="form.arbiter3_name" list="fideNames" @change="handleArbiterChange('arbiter3_name', 'arbiter3_fide_id')"></label>
      <label><span>{{ tField('arbiter3_fide_id') }}</span><input type="text" v-model="form.arbiter3_fide_id"></label>
      <label><span>{{ tField('arbiter4_name') }}</span><input type="text" v-model="form.arbiter4_name" list="fideNames" @change="handleArbiterChange('arbiter4_name', 'arbiter4_fide_id')"></label>
      <label><span>{{ tField('arbiter4_fide_id') }}</span><input type="text" v-model="form.arbiter4_fide_id"></label>
      
      <div style="grid-column: 1 / -1; font-size: 0.85rem; color: var(--muted); margin-top: -0.25rem; font-style: italic;">{{ tUI('more_arbiters_note') }}</div>

      <div class="group-title">{{ tCat('organizers') }}</div>

      <label><span class="required-label">{{ tField('chief_organizer_name') }}</span><input type="text" v-model="form.chief_organizer_name" required></label>
      <label><span class="required-label">{{ tField('chief_organizer_fide_id') }}</span><input type="text" v-model="form.chief_organizer_fide_id" required></label>
      <label><span>{{ tField('organizer1_name') }}</span><input type="text" v-model="form.organizer1_name"></label>
      <label><span>{{ tField('organizer1_fide_id') }}</span><input type="text" v-model="form.organizer1_fide_id"></label>
      <label><span>{{ tField('organizer2_name') }}</span><input type="text" v-model="form.organizer2_name"></label>
      <label><span>{{ tField('organizer2_fide_id') }}</span><input type="text" v-model="form.organizer2_fide_id"></label>
      <label><span>{{ tField('organizer3_name') }}</span><input type="text" v-model="form.organizer3_name"></label>
      <label><span>{{ tField('organizer3_fide_id') }}</span><input type="text" v-model="form.organizer3_fide_id"></label>

      <div class="group-title">{{ tCat('time_control') }}</div>

      <label>
        <span class="required-label">{{ tField('time_control_code') }}</span>
        <select v-model="form.time_control_code" required>
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="t in lookups.time_control_types" :key="t" :value="t">{{ t }}</option>
        </select>
      </label>
      <label>
        <span class="required-label">{{ tField('time_control_desc') }}</span>
        <select v-model="form.time_control_desc" required>
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="opt in timeControlDescOptions" :key="opt" :value="opt">{{ opt }}</option>
          <option value="Other">Other</option>
        </select>
      </label>
      
      <div v-if="form.time_control_desc === 'Other'">
        <label><span class="required-label">{{ tField('timectl_other_desc') }}</span><textarea v-model="form.timectl_other_desc" required></textarea></label>
        <label><span class="required-label">{{ tField('timectl1_moves') }}</span><input type="number" v-model="form.timectl1_moves" min="0" required></label>
        <label><span class="required-label">{{ tField('timectl1_minutes') }}</span><input type="number" v-model="form.timectl1_minutes" min="0" required></label>
        <label><span class="required-label">{{ tField('timectl1_inc_type') }}</span>
          <select v-model="form.timectl1_inc_type" required>
            <option value="">{{ tUI('select_placeholder') }}</option>
            <option v-for="opt in lookups.inc_delay_options" :key="opt" :value="opt">{{ tOptInc(opt) }}</option>
          </select>
        </label>
        <label><span class="required-label">{{ tField('timectl1_inc_seconds') }}</span><input type="number" v-model="form.timectl1_inc_seconds" min="0" required></label>
        
        <label><span class="required-label">{{ tField('timectl2_moves') }}</span><input type="number" v-model="form.timectl2_moves" min="0" required></label>
        <label><span class="required-label">{{ tField('timectl2_minutes') }}</span><input type="number" v-model="form.timectl2_minutes" min="0" required></label>
        <label><span class="required-label">{{ tField('timectl2_inc_type') }}</span>
          <select v-model="form.timectl2_inc_type" required>
            <option value="">{{ tUI('select_placeholder') }}</option>
            <option v-for="opt in lookups.inc_delay_options" :key="opt" :value="opt">{{ tOptInc(opt) }}</option>
          </select>
        </label>
        <label><span class="required-label">{{ tField('timectl2_inc_seconds') }}</span><input type="number" v-model="form.timectl2_inc_seconds" min="0" required></label>
        
        <label><span class="required-label">{{ tField('timectl_final_minutes') }}</span><input type="number" v-model="form.timectl_final_minutes" min="0" required></label>
        <label><span class="required-label">{{ tField('timectl_final_inc_type') }}</span>
          <select v-model="form.timectl_final_inc_type" required>
            <option value="">{{ tUI('select_placeholder') }}</option>
            <option v-for="opt in lookups.inc_delay_options" :key="opt" :value="opt">{{ tOptInc(opt) }}</option>
          </select>
        </label>
        <label><span class="required-label">{{ tField('timectl_final_inc_seconds') }}</span><input type="number" v-model="form.timectl_final_inc_seconds" min="0" required></label>
      </div>

      <div class="group-title">{{ tCat('other_parameters') }}</div>

      <label><span>{{ tField('max_rating') }}</span><input type="number" v-model="form.max_rating" min="0"></label>
      <label>
        <span>{{ tField('age_limit') }}</span>
        <select v-model="form.age_limit">
          <option v-for="opt in lookups.age_limit_options" :key="opt" :value="opt">{{ tOptAge(opt) }}</option>
        </select>
      </label>
      <label v-if="form.age_limit && form.age_limit !== 'None'">
        <span class="required-label">{{ tField('age_limit_value') }}</span><input type="number" v-model="form.age_limit_value" min="0" required>
      </label>

      <label>
        <span class="required-label">{{ tField('all_digital_clocks') }}</span>
        <select v-model="form.all_digital_clocks" required>
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="opt in lookups.yes_no" :key="opt" :value="opt">{{ tOptYesNo(opt) }}</option>
        </select>
      </label>
      <label>
        <span>{{ tField('internet_tx') }}</span>
        <select v-model="form.internet_tx">
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="opt in lookups.yes_no" :key="opt" :value="opt">{{ tOptYesNo(opt) }}</option>
        </select>
      </label>
      <label v-if="form.internet_tx === 'Yes'">
        <span class="required-label">{{ tField('internet_tx_boards') }}</span><input type="number" v-model="form.internet_tx_boards" min="1" required>
      </label>

      <label>
        <span class="required-label">{{ tField('tiebreak_method') }}</span>
        <select v-model="form.tiebreak_method" required>
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="opt in lookups.tiebreak_options" :key="opt" :value="opt">{{ opt }}</option>
        </select>
      </label>
      <label v-if="form.tiebreak_method === 'Other'">
        <span class="required-label">{{ tField('tiebreak_other') }}</span><input type="text" v-model="form.tiebreak_other" required>
      </label>

      <label>
        <span class="required-label">{{ tField('software') }}</span>
        <select v-model="form.software" required>
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="opt in lookups.software_options" :key="opt" :value="opt">{{ opt }}</option>
        </select>
      </label>
      <label v-if="form.software === 'Other'">
        <span class="required-label">{{ tField('software_other') }}</span><input type="text" v-model="form.software_other" required>
      </label>

      <label><span class="required-label">{{ tField('software_version') }}</span><input type="text" v-model="form.software_version" required></label>
      
      <label>
        <span>{{ tField('pgn_provided') }}</span>
        <select v-model="form.pgn_provided">
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="opt in lookups.yes_no" :key="opt" :value="opt">{{ tOptYesNo(opt) }}</option>
        </select>
      </label>
      
      <label><span class="required-label">{{ tField('contact_email') }}</span><input type="email" v-model="form.contact_email" required></label>
      <label>
        <span class="required-label">{{ tField('homepage') }}</span>
        <input type="text" v-model="form.homepage" required>
        <div v-if="form.homepage && !form.homepage.includes('http')" style="color:var(--error); font-size:0.85rem; margin-top:0.25rem;">
          Warning: URL should usually contain http or https.
        </div>
      </label>
      <label><span>{{ tField('prize_fund') }}</span><input type="number" v-model="form.prize_fund" min="0.01" step="0.01"></label>
      <label><span>{{ tField('remarks') }}</span><textarea v-model="form.remarks"></textarea></label>

      <button type="submit">{{ tUI('export_btn') }}</button>

      <datalist id="fideNames">
        <option v-for="name in lookups.fide_names" :key="name" :value="name"></option>
      </datalist>
    </form>
  </div>
</template>

<style>
html {
  --bg: #f5f5f7;
  --text: #111827;
  --muted: #4b5563;
  --card-bg: #ffffff;
  --border: #e5e7eb;
  --accent: #2563eb;
  --accent-soft: #eff6ff;
  --error: #b91c1c;
  --focus-ring: #93c5fd;
}
html[data-theme="dark"] {
  --bg: #020617;
  --text: #e5e7eb;
  --muted: #9ca3af;
  --card-bg: #020617;
  --border: #1f2937;
  --accent: #60a5fa;
  --accent-soft: #0b1120;
  --error: #fca5a5;
  --focus-ring: #38bdf8;
}
body, .v-application {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  margin: 0;
  padding: 0;
}
</style>

<style scoped>

.form-shell {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  max-width: 900px;
  margin: 2rem auto;
  background-color: var(--card-bg, #ffffff);
  color: var(--text, #111827);
  border-radius: 0.75rem;
  border: 1px solid var(--border, #e5e7eb);
  padding: 1.75rem 1.75rem 1.5rem;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.18);
}

.shell-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.35rem;
}
.header-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.lang-selector {
  display: flex;
  gap: 0.25rem;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 999px;
  padding: 0.2rem;
  background-color: var(--card-bg, #ffffff);
}
.lang-btn {
  text-decoration: none;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--muted, #4b5563);
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  transition: all 0.2s;
}
.lang-btn:hover {
  color: var(--text, #111827);
  background-color: var(--accent-soft, #eff6ff);
}
.lang-btn.active {
  color: #ffffff !important;
  background-color: var(--accent, #2563eb);
}
h1 { margin: 0; font-size: 1.35rem; letter-spacing: 0.02em; }
.note { margin: 0 0 1rem; font-size: 0.9rem; color: var(--muted, #4b5563); }
.note--dark { display: none; }
[data-theme="dark"] .note--light { display: none; }
[data-theme="dark"] .note--dark { display: block; }
.warning {
  margin: 0 0 1rem;
  padding: 0.75rem 0.9rem;
  border-radius: 0.5rem;
  border: 1px solid #f59e0b;
  background: #fffbeb;
  color: #92400e;
  font-size: 0.92rem;
}
[data-theme="dark"] .warning {
  background: #271800;
  color: #fcd34d;
  border-color: #d97706;
}
.error { color: var(--error, #b91c1c); margin-bottom: 1rem; font-weight: 600; font-size: 0.95rem; }
.theme-toggle {
  padding: 0.25rem 0.75rem;
  font-size: 0.8rem;
  border-radius: 999px;
  border: 1px solid var(--border, #e5e7eb);
  background-color: var(--card-bg, #ffffff);
  color: var(--muted, #4b5563);
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  cursor: pointer;
}
.theme-toggle:hover { background-color: var(--accent-soft, #eff6ff); color: var(--text, #111827); }
.theme-toggle span.icon { font-size: 0.95rem; }
form { display: grid; grid-template-columns: 1fr; gap: 0.75rem; }
label { display: block; font-size: 0.95rem; padding-left: 0; border-left: 0 solid transparent; }
[data-theme="dark"] label:has(.required-label) { border-left: 3px solid var(--accent, #60a5fa); padding-left: 0.5rem; }
label span { display: block; margin-bottom: 0.25rem; font-weight: 400; }
label span.required-label { font-weight: 700; }
input, textarea, select {
  width: 100%;
  padding: 0.4rem 0.5rem;
  font: inherit;
  box-sizing: border-box;
  border-radius: 0.375rem;
  border: 1px solid var(--border, #e5e7eb);
  background-color: var(--card-bg, #ffffff);
  color: var(--text, #111827);
}
input:focus, textarea:focus, select:focus { outline: 2px solid var(--focus-ring, #93c5fd); outline-offset: 1px; }
.input-error { border-color: var(--error, #b91c1c) !important; }
textarea { min-height: 4rem; }
.group-title { margin-top: 1.5rem; font-weight: 700; font-size: 0.98rem; color: var(--muted, #4b5563); }
button[type="submit"] {
  margin-top: 1.5rem;
  padding: 0.6rem 1.2rem;
  font-weight: 600;
  border-radius: 999px;
  border: none;
  background-color: var(--accent, #2563eb);
  color: #ffffff;
  cursor: pointer;
}
button[type="submit"]:hover { background-color: #1d4ed8; }
button[type="submit"]:focus-visible { outline: 2px solid var(--focus-ring, #93c5fd); outline-offset: 2px; }
.hidden { display: none; }
.round-row.active { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
[data-theme="dark"] input[type="date"]::-webkit-calendar-picker-indicator { filter: invert(1); opacity: 0.9; cursor: pointer; }
@media (max-width: 640px) {
  .form-shell { padding: 1.25rem 1.25rem 1.1rem; }
  .round-row.active { grid-template-columns: 1fr; }
}
</style>

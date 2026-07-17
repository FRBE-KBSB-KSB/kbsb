<script setup>
import { ref, onMounted, computed, watch } from "vue";
import { useRoute } from "vue-router";

// communication
const { $backend } = useNuxtApp()
const route = useRoute()

// State
const queryLang = route.query.locale || route.query.lang;
const lang = ref(["en", "nl", "fr"].includes(queryLang) ? queryLang : "en");
const waitingdialog = ref(false);
const errorText = ref("");
const submitted = ref(false);

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
  national_championship_143a: "No",
  on_fide_calendar: "No",
  tournament_report: "",
  tournament_type: "Over the Board",
  event_name: "",
  city: "",
  country: "BEL",
  expected_players: "",
  tournament_system: "",
  rounds_reported: "",
  multiple_round_days: "0",
  female_only: "",
  start_date: "",
  end_date: "",
  title_norms: "No",
  gm_wgm_norms: "No",
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
  all_digital_clocks: "Yes",
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

const eventNameHasIllegalChars = computed(() =>
  form.value.event_name ? /[^A-Za-z0-9 ]/.test(form.value.event_name) : false
);

const timeControlDescOptions = computed(() => {
  if (!form.value.time_control_code) return [];
  return lookups.value.time_control_desc[form.value.time_control_code] || [];
});

const totalMinutes = computed(() => {
  if (form.value.time_control_code !== 'Standard') return 0;
  
  if (form.value.time_control_desc === 'Other') {
    const m1 = parseInt(form.value.timectl1_minutes, 10) || 0;
    const m2 = parseInt(form.value.timectl2_minutes, 10) || 0;
    const m3 = parseInt(form.value.timectl_final_minutes, 10) || 0;
    const inc = parseInt(form.value.timectl1_inc_seconds, 10) || 0;
    return m1 + m2 + m3 + inc;
  }
  
  const desc = form.value.time_control_desc;
  if (!desc) return 0;
  
  let totalMins = 0;
  const minMatches = desc.matchAll(/(\d+)min/g);
  for (const m of minMatches) {
    totalMins += parseInt(m[1], 10);
  }
  
  let incMins = 0;
  const incMatch = desc.match(/(\d+)sec\/move(?: from move (\d+))?/);
  if (incMatch) {
    const sec = parseInt(incMatch[1], 10);
    const startMove = incMatch[2] ? parseInt(incMatch[2], 10) : 1;
    if (startMove === 1) {
      incMins = sec;
    } else if (startMove < 60) {
      incMins = (sec * (60 - startMove)) / 60;
    }
  }
  
  return totalMins + incMins;
});

const ratingRequirement = computed(() => {
  if (form.value.time_control_code !== 'Standard') return 'ok';
  const mins = totalMinutes.value;
  if (mins <= 0) return 'ok';
  
  if (mins < 60) {
    return 'not_rateable';
  } else if (mins < 90) {
    const val = parseInt(form.value.max_rating, 10);
    return (!isNaN(val) && val < 1800) ? 'ok' : 'require_1800';
  } else if (mins < 120) {
    const val = parseInt(form.value.max_rating, 10);
    return (!isNaN(val) && val < 2400) ? 'ok' : 'require_2400';
  }
  return 'ok';
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
  return { year: periodYear, month: periodMonth, key: `${periodYear}-${String(periodMonth).padStart(2, '0')}` };
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
const noLicenseArbiters = ref(new Set())

const fide_people_by_id = computed(() => {
  const map = {}
  for (const [name, info] of Object.entries(lookups.value.fide_people || {})) {
    if (info.id) map[String(info.id)] = { ...info, name }
  }
  return map
})

function handleArbiterChange(nameField, idField) {
  const name = form.value[nameField];
  const info = lookups.value.fide_people[name];
  const updated = new Set(noLicenseArbiters.value)
  updated.delete(nameField)
  if (info) {
    form.value[idField] = info.id || "";
    if (info.license && info.license.toLowerCase() === 'no license') {
      updated.add(nameField)
    }
  }
  noLicenseArbiters.value = updated
}

function handleArbiterIdChange(nameField, idField) {
  const id = String(form.value[idField] || '').trim()
  if (!id) return
  const info = fide_people_by_id.value[id]
  const updated = new Set(noLicenseArbiters.value)
  updated.delete(nameField)
  if (info) {
    form.value[nameField] = info.name || ""
    if (info.license && info.license.toLowerCase() === 'no license') {
      updated.add(nameField)
    }
  }
  noLicenseArbiters.value = updated
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
  if (ratingRequirement.value !== 'ok') {
    let confirmKey = '';
    if (ratingRequirement.value === 'not_rateable') confirmKey = 'fide_under_60_confirm';
    else if (ratingRequirement.value === 'require_1800') confirmKey = 'fide_under_90_confirm';
    else if (ratingRequirement.value === 'require_2400') confirmKey = 'fide_under_120_confirm';
    
    if (confirmKey) {
      const proceed = confirm(tMsg(confirmKey));
      if (!proceed) return;
    }
  }
  waitingdialog.value = true;
  errorText.value = "";
  try {
    const response = await $backend("fide", "generate", {
      locale: lang.value,
      formdata: form.value,
    })
    console.log("reponse on generate", response)
    submitted.value = true;
    if (process.client) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

  } catch (error) {
    console.error(error);
    errorText.value = "Error submitting form";
  } finally {
    waitingdialog.value = false;
  }
}

function resetForm() {
  form.value = {
    invoice_email: "",
    invoice_clubnr: "",
    fide_laws_followed: "Yes",
    national_championship_143a: "No",
    on_fide_calendar: "No",
    tournament_report: "",
    tournament_type: "Over the Board",
    event_name: "",
    city: "",
    country: "BEL",
    expected_players: "",
    tournament_system: "",
    rounds_reported: "",
    multiple_round_days: "0",
    female_only: "",
    start_date: "",
    end_date: "",
    title_norms: "No",
    gm_wgm_norms: "No",
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
    all_digital_clocks: "Yes",
    internet_tx: "", internet_tx_boards: "",
    tiebreak_method: "", tiebreak_other: "",
    software: "", software_other: "", software_version: "",
    pgn_provided: "No",
    contact_email: "", homepage: "", prize_fund: "", remarks: ""
  };
  for (let i = 1; i <= 100; i++) {
    form.value[`round${i}_date`] = "";
    form.value[`round${i}_report`] = "";
  }
  submitted.value = false;
}
onMounted(() => {
  loadFormData();
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
  <div v-else-if="submitted" class="form-shell" style="text-align: center; padding: 3.5rem 2rem; display: flex; flex-direction: column; align-items: center; justify-content: center;">
    <div style="width: 80px; height: 80px; background-color: #10b981; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 3rem; margin-bottom: 2rem; box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);">✓</div>
    <h2 style="font-size: 1.6rem; font-weight: 700; color: var(--text, #111827); margin-bottom: 1rem;">
      {{ tUI('submitted_title') }}
    </h2>
    <p style="font-size: 1.05rem; color: var(--muted, #4b5563); max-width: 600px; margin: 0 auto 2.5rem; line-height: 1.6;">
      {{ tUI('submitted_msg') }}
    </p>
    <button @click="resetForm" style="padding: 0.6rem 1.8rem; font-weight: 600; border-radius: 999px; border: none; background-color: var(--accent, #2563eb); color: #ffffff; cursor: pointer; transition: background-color 0.2s;">
      {{ tUI('back_btn') }}
    </button>
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
      </div>
    </div>

    <p class="note" v-html="tUI('mandatory_note')"></p>
    
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
        <input type="text" v-model="form.event_name" :class="{ 'input-error': eventNameHasIllegalChars }" required>
        <div v-if="eventNameHasIllegalChars" style="color: var(--error); font-size: 0.85rem; margin-top: 0.25rem; font-weight: 600;">
          ⚠ Illegal characters detected. Only letters A–Z, numbers, and spaces are allowed.
        </div>
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
        <span v-if="noLicenseArbiters.has('chief_arbiter_name')" style="color: var(--error); font-size: 0.85rem; font-weight: 700;">⚠ No license</span>
      </label>
      <label><span class="required-label">{{ tField('chief_arbiter_fide_id') }}</span><input type="text" v-model="form.chief_arbiter_fide_id" @change="handleArbiterIdChange('chief_arbiter_name', 'chief_arbiter_fide_id')" required></label>
      
      <label><span>{{ tField('dep_chief_arbiter1_name') }}</span>
        <input type="text" v-model="form.dep_chief_arbiter1_name" list="fideNames" @change="handleArbiterChange('dep_chief_arbiter1_name', 'dep_chief_arbiter1_fide_id')">
        <span v-if="noLicenseArbiters.has('dep_chief_arbiter1_name')" style="color: var(--error); font-size: 0.85rem; font-weight: 700;">⚠ No license</span>
      </label>
      <label><span>{{ tField('dep_chief_arbiter1_fide_id') }}</span><input type="text" v-model="form.dep_chief_arbiter1_fide_id" @change="handleArbiterIdChange('dep_chief_arbiter1_name', 'dep_chief_arbiter1_fide_id')"></label>
      
      <label><span>{{ tField('dep_chief_arbiter2_name') }}</span>
        <input type="text" v-model="form.dep_chief_arbiter2_name" list="fideNames" @change="handleArbiterChange('dep_chief_arbiter2_name', 'dep_chief_arbiter2_fide_id')">
        <span v-if="noLicenseArbiters.has('dep_chief_arbiter2_name')" style="color: var(--error); font-size: 0.85rem; font-weight: 700;">⚠ No license</span>
      </label>
      <label><span>{{ tField('dep_chief_arbiter2_fide_id') }}</span><input type="text" v-model="form.dep_chief_arbiter2_fide_id" @change="handleArbiterIdChange('dep_chief_arbiter2_name', 'dep_chief_arbiter2_fide_id')"></label>
      
      <label>
        <span>{{ tField('kind_of_arbiters') }}</span>
        <select v-model="form.kind_of_arbiters">
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="opt in lookups.kind_of_arbiters_options" :key="opt" :value="opt">{{ opt }}</option>
        </select>
      </label>
      
      <label>
        <span>{{ tField('arbiter1_name') }}</span>
        <input type="text" v-model="form.arbiter1_name" list="fideNames" @change="handleArbiterChange('arbiter1_name', 'arbiter1_fide_id')">
        <span v-if="noLicenseArbiters.has('arbiter1_name')" style="color: var(--error); font-size: 0.85rem; font-weight: 700;">⚠ No license</span>
      </label>
      <label><span>{{ tField('arbiter1_fide_id') }}</span><input type="text" v-model="form.arbiter1_fide_id" @change="handleArbiterIdChange('arbiter1_name', 'arbiter1_fide_id')"></label>
      <label>
        <span>{{ tField('arbiter2_name') }}</span>
        <input type="text" v-model="form.arbiter2_name" list="fideNames" @change="handleArbiterChange('arbiter2_name', 'arbiter2_fide_id')">
        <span v-if="noLicenseArbiters.has('arbiter2_name')" style="color: var(--error); font-size: 0.85rem; font-weight: 700;">⚠ No license</span>
      </label>
      <label><span>{{ tField('arbiter2_fide_id') }}</span><input type="text" v-model="form.arbiter2_fide_id" @change="handleArbiterIdChange('arbiter2_name', 'arbiter2_fide_id')"></label>
      <label>
        <span>{{ tField('arbiter3_name') }}</span>
        <input type="text" v-model="form.arbiter3_name" list="fideNames" @change="handleArbiterChange('arbiter3_name', 'arbiter3_fide_id')">
        <span v-if="noLicenseArbiters.has('arbiter3_name')" style="color: var(--error); font-size: 0.85rem; font-weight: 700;">⚠ No license</span>
      </label>
      <label><span>{{ tField('arbiter3_fide_id') }}</span><input type="text" v-model="form.arbiter3_fide_id" @change="handleArbiterIdChange('arbiter3_name', 'arbiter3_fide_id')"></label>
      <label>
        <span>{{ tField('arbiter4_name') }}</span>
        <input type="text" v-model="form.arbiter4_name" list="fideNames" @change="handleArbiterChange('arbiter4_name', 'arbiter4_fide_id')">
        <span v-if="noLicenseArbiters.has('arbiter4_name')" style="color: var(--error); font-size: 0.85rem; font-weight: 700;">⚠ No license</span>
      </label>
      <label><span>{{ tField('arbiter4_fide_id') }}</span><input type="text" v-model="form.arbiter4_fide_id" @change="handleArbiterIdChange('arbiter4_name', 'arbiter4_fide_id')"></label>
      
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

      <label>
        <span>{{ tField('max_rating') }}</span>
        <input type="number" v-model="form.max_rating" min="0">
        <div v-if="ratingRequirement === 'not_rateable'" style="color: #ef4444; font-size: 0.85rem; margin-top: 0.25rem; font-weight: 600;">
          {{ tUI('fide_under_60_warning') }}
        </div>
        <div v-else-if="ratingRequirement === 'require_1800'" style="color: #d97706; font-size: 0.85rem; margin-top: 0.25rem; font-weight: 500;">
          {{ tUI('fide_under_90_warning') }}
        </div>
        <div v-else-if="ratingRequirement === 'require_2400'" style="color: #d97706; font-size: 0.85rem; margin-top: 0.25rem; font-weight: 500;">
          {{ tUI('fide_under_120_warning') }}
        </div>
      </label>
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

      <label><span>{{ tField('software_version') }}</span><input type="text" v-model="form.software_version"></label>
      
      <label>
        <span>{{ tField('pgn_provided') }}</span>
        <select v-model="form.pgn_provided">
          <option value="">{{ tUI('select_placeholder') }}</option>
          <option v-for="opt in lookups.yes_no" :key="opt" :value="opt">{{ tOptYesNo(opt) }}</option>
        </select>
      </label>
      
      <label>
        <span class="required-label">{{ tField('contact_email') }}</span>
        <input type="email" v-model="form.contact_email" required>
        <div style="font-size: 0.82rem; color: var(--muted); margin-top: 0.2rem; font-style: italic;">A confirmation email will be sent to this address. This is typically the email of the organising club.</div>
      </label>
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
  --bg: #ffffff;
  --text: #111827;
  --muted: #4b5563;
  --card-bg: #ffffff;
  --border: #e5e7eb;
  --accent: #2563eb;
  --accent-soft: #eff6ff;
  --error: #b91c1c;
  --focus-ring: #93c5fd;
  overflow-y: auto !important;
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

.warning {
  margin: 0 0 1rem;
  padding: 0.75rem 0.9rem;
  border-radius: 0.5rem;
  border: 1px solid #f59e0b;
  background: #fffbeb;
  color: #92400e;
  font-size: 0.92rem;
}

.error { color: var(--error, #b91c1c); margin-bottom: 1rem; font-weight: 600; font-size: 0.95rem; }

form { display: grid; grid-template-columns: 1fr; gap: 0.75rem; }
label { display: block; font-size: 0.95rem; padding-left: 0; border-left: 0 solid transparent; }

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

@media (max-width: 640px) {
  .form-shell { padding: 1.25rem 1.25rem 1.1rem; }
  .round-row.active { grid-template-columns: 1fr; }
}
</style>

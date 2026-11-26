<script setup>
// One player's details on the registration form: the search first, then the
// fields it fills in, every required one marked with a * from the start. Used
// for a player registering alone and for each player of a team (the page
// puts its own contact fields in the "contact" slot).
//
// Organisers' feedback, 26 Nov 2026: a parent did not know the FIDE ID or
// national number, missed that the search would fill them in, and was refused
// for having no category. So the search comes first with a line saying so,
// sex has no default, the national number says the search fills it in, the
// club is picked from the club list, and the category is chosen from the
// birth year.
//
// Luc's remarks, 26 Nov 2026: the birth date is typed (a day, or a year
// alone, which is 1 January of it) and a search pick fills 1 January of the
// year it found when nothing is typed yet; no "no match" line right after a
// pick; a team's later boards and reserves are optional, so their rules only
// apply once something is filled in.

import { ref, computed, watch } from "vue"
import { useI18n } from "vue-i18n"
import { categoryRanges, categoryDisplay, categoryForBirthYear, birthYearOf } from "@/util/trnreg_categories"
import { parseBirthInput, formatBirthInput, birthDateFromYear } from "@/util/trnreg_form"

// Number fields keep only digits (see the page for why not type="number").
const vDigits = {
  mounted(el) {
    const input = el.tagName === "INPUT" ? el : el.querySelector("input")
    if (!input) return
    input.setAttribute("inputmode", "numeric")
    input.addEventListener("input", () => {
      const clean = input.value.replace(/\D/g, "")
      if (clean !== input.value) {
        input.value = clean
        input.dispatchEvent(new Event("input"))
      }
    })
  },
}

const props = defineProps({
  // The registration being filled in; its fields are set in place.
  player: { type: Object, required: true },
  tournament: { type: Object, required: true },
  clubs: { type: Array, default: () => [] },
  // "Board 2" above a team's player; nothing for a single registration.
  heading: { type: String, default: "" },
  // A team's player beyond the first: may stay empty, checked once filled.
  optional: { type: Boolean, default: false },
})

const { t } = useI18n()
const { $backend } = useNuxtApp()

const p = props.player

const req = (key) => `${t(key)} *`
// Something typed that says who the player is; an optional slot without it
// is left out of the team.
const filled = computed(() => ["last_name", "first_name", "national_id", "fide_id"].some((k) => String(p[k] ?? "").trim() !== ""))
const requiredRule = (v) => (props.optional && !filled.value) || (v !== null && v !== undefined && String(v).trim() !== "") || t("trnreg.rule_required")

// ---- search -------------------------------------------------------------

const lookupQuery = ref("")
const lookupResults = ref([])
const lookupSearching = ref(false)
// Just picked: the box holds the picked name, which is no new search.
const picked = ref(false)
let lookupTimer = null

function onLookupInput() {
  picked.value = false
  clearTimeout(lookupTimer)
  const q = lookupQuery.value
  if (!q || q.trim().length < 2) {
    lookupResults.value = []
    return
  }
  lookupTimer = setTimeout(async () => {
    lookupSearching.value = true
    try {
      const reply = await $backend("tournament_registrations", "lookup", { id: props.tournament.id, q })
      // a slower earlier keystroke can resolve after a later one
      if (lookupQuery.value !== q) return
      lookupResults.value = (reply.data && reply.data.players) || []
    } catch (error) {
      if (lookupQuery.value === q) lookupResults.value = []
    } finally {
      if (lookupQuery.value === q) lookupSearching.value = false
    }
  }, 300)
}

const clubById = computed(() => {
  const m = new Map()
  for (const c of props.clubs) m.set(Number(c.idclub), c)
  return m
})

function clubName(id) {
  const c = clubById.value.get(Number(id))
  return c ? c.name_short || c.name_long || "" : ""
}

function selectLookupResult(r) {
  p.last_name = r.last_name || ""
  p.first_name = r.first_name || ""
  p.sex = r.sex || null
  p.national_id = r.national_id || ""
  p.national_club = r.club || ""
  p.national_club_name = r.club_name || clubName(r.club)
  // Shown, not edited: the server reads both from our records on submit.
  p.affiliated = r.affiliated === true ? true : (r.affiliated === false ? false : null)
  p.g_license = r.g_license === true
  p.fide_id = r.fide_id || ""
  p.fide_rating_standard = r.fide_rating_standard || ""
  p.fide_rating_rapid = r.fide_rating_rapid || ""
  p.fide_rating_blitz = r.fide_rating_blitz || ""
  p.fide_title = r.fide_title || ""
  p.fide_federation = r.fide_federation || ""
  p.nationality = r.fide_federation || ""
  // Only the year comes back, never a date. It is sent along so the API can
  // pick the category from it, and stands as 1 January of it in the date box
  // when nothing is typed there (or only an earlier pick's year was).
  p.birth_year = r.birth_year || null
  if (!p.date_birth || birthFromYear.value) {
    p.date_birth = birthDateFromYear(r.birth_year)
    birthFromYear.value = !!p.date_birth
    birthText.value = formatBirthInput(p.date_birth)
  }
  lookupQuery.value = r.name || `${r.first_name} ${r.last_name}`
  lookupResults.value = []
  picked.value = true
}

// ---- birth date ---------------------------------------------------------

// Typed as 31/12/2009 or as a year alone; stored as YYYY-MM-DD.
const birthText = ref(formatBirthInput(p.date_birth))
const birthFromYear = ref(false)
watch(
  () => p.date_birth,
  (v) => {
    if (parseBirthInput(birthText.value) !== (v || "")) birthText.value = formatBirthInput(v)
  }
)
function onBirthInput(v) {
  birthText.value = v
  birthFromYear.value = false
  const parsed = parseBirthInput(v)
  if (parsed !== null) p.date_birth = parsed
}
const birthFormatRule = (v) => parseBirthInput(v) !== null || t("trnreg.rule_birth_date_format")

// ---- fields -------------------------------------------------------------

const hasFideId = computed(() => String(p.fide_id || "").trim() !== "")
const birthDateRule = (v) => hasFideId.value || requiredRule(v)
const needsFideIdWarning = computed(() => !!props.tournament.fide_homologated && !hasFideId.value)

function yesNoUnknown(v) {
  if (v === true) return t("trnreg.yes")
  if (v === false) return t("trnreg.no")
  return "-"
}

const sexItems = computed(() => [
  { title: t("trnreg.sex_m"), value: "M" },
  { title: t("trnreg.sex_f"), value: "F" },
])

const FEDERATION_RE = /^[A-Z]{3}$/
const federationRule = (v) => !v || FEDERATION_RE.test(v) || t("trnreg.rule_federation_code")
function federationInput(v) {
  return String(v || "").toUpperCase().replace(/[^A-Z]/g, "").slice(0, 3)
}
const FIDE_TITLES = ["GM", "IM", "FM", "CM", "WGM", "WIM", "WFM", "WCM", "AGM", "AIM", "AFM", "ACM"]
const fideTitleItems = computed(() => [
  { title: t("trnreg.title_none"), value: "" },
  ...FIDE_TITLES.map((code) => ({ title: code, value: code })),
])

const RATING_FIELD = { Std: "fide_rating_standard", Rapid: "fide_rating_rapid", Blitz: "fide_rating_blitz" }
const ratingField = computed(() => RATING_FIELD[props.tournament.time_control] || "fide_rating_standard")

// The club list, number and name, searchable by either. A number the list
// does not hold (a club since gone) still shows as itself.
const clubItems = computed(() =>
  [...props.clubs]
    .sort((a, b) => Number(a.idclub) - Number(b.idclub))
    .map((c) => ({ title: `${c.idclub} ${c.name_short || c.name_long || ""}`.trim(), value: Number(c.idclub) }))
)
const clubModel = computed({
  get: () => (p.national_club === "" || p.national_club === null || p.national_club === undefined ? null : Number(p.national_club)),
  set: (v) => {
    p.national_club = v === null || v === undefined || v === "" ? "" : Number(v)
    p.national_club_name = p.national_club === "" ? "" : clubName(v)
  },
})

// ---- category -----------------------------------------------------------

const ranges = computed(() => categoryRanges(props.tournament))
const categoryItems = computed(() => ranges.value.map((r) => ({ title: categoryDisplay(r, t), value: r.index })))
const manyCategories = computed(() => ranges.value.length > 1)

// Picked from the birth year until somebody picks one by hand.
const categoryAuto = ref(false)
watch(
  () => [p.date_birth, p.birth_year, ranges.value.length],
  () => {
    if (!manyCategories.value) return
    if (p.category_index !== "" && p.category_index !== null && !categoryAuto.value) return
    const index = categoryForBirthYear(props.tournament, birthYearOf(p))
    if (index === null) return
    p.category_index = index
    categoryAuto.value = true
  },
  { immediate: true }
)
function pickCategory(v) {
  p.category_index = v
  categoryAuto.value = false
}
</script>

<template>
  <div>
    <div v-if="heading" class="text-subtitle-1 font-weight-bold text-green-darken-3 mb-2">{{ heading }}</div>

    <!-- The search first: it fills in nearly everything below. -->
    <v-sheet class="trnreg-search-first pa-3 mb-4" rounded>
      <div class="text-body-2 font-weight-medium mb-2">
        <v-icon size="small" color="green-darken-2" class="mr-1">mdi-account-search</v-icon>{{ t('trnreg.search_first') }}
      </div>
      <div class="trnreg-lookup-wrap">
        <v-text-field
          v-model="lookupQuery"
          :label="t('trnreg.field_lookup')"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          color="green-darken-2"
          density="comfortable"
          bg-color="white"
          autocomplete="off"
          :hint="t('trnreg.lookup_hint')"
          persistent-hint
          @input="onLookupInput"
          @blur="lookupResults = []"
        ></v-text-field>
        <span v-if="lookupSearching" class="trnreg-searching-hint">{{ t('trnreg.lookup_searching') }}</span>
        <ul v-if="lookupResults.length" class="trnreg-dropdown">
          <li v-for="r in lookupResults" :key="r.national_id || r.fide_id || r.name" @mousedown.prevent="selectLookupResult(r)">
            {{ r.name }}
            <span class="trnreg-dropdown-meta">{{ r.birth_year || '' }} {{ r.club ? `${r.club} ${clubName(r.club)}` : '' }}</span>
          </li>
        </ul>
        <div v-if="!picked && !lookupSearching && lookupQuery.trim().length >= 2 && !lookupResults.length" class="trnreg-searching-hint">{{ t('trnreg.lookup_no_results') }}</div>
      </div>
    </v-sheet>

    <v-row dense>
      <v-col cols="12" sm="6">
        <v-text-field v-model="p.last_name" :label="req('trnreg.field_last_name')" variant="outlined" color="green-darken-2" density="compact" class="trnreg-required" :rules="[requiredRule]"></v-text-field>
      </v-col>
      <v-col cols="12" sm="6">
        <v-text-field v-model="p.first_name" :label="req('trnreg.field_first_name')" variant="outlined" color="green-darken-2" density="compact" class="trnreg-required" :rules="[requiredRule]"></v-text-field>
      </v-col>
      <v-col cols="12" sm="4">
        <!-- No default: nobody is registered as M because the box started there. -->
        <v-select v-model="p.sex" :items="sexItems" item-title="title" item-value="value" :label="req('trnreg.field_sex')" :placeholder="t('trnreg.sex_placeholder')" persistent-placeholder variant="outlined" color="green-darken-2" density="compact" class="trnreg-required" :rules="[requiredRule]"></v-select>
      </v-col>
      <v-col cols="12" sm="4">
        <v-text-field
          :model-value="birthText" @update:model-value="onBirthInput"
          :label="hasFideId ? t('trnreg.field_date_birth') : req('trnreg.field_date_birth')"
          :placeholder="t('trnreg.birth_date_placeholder')" persistent-placeholder
          variant="outlined" color="green-darken-2" density="compact" autocomplete="off"
          :class="hasFideId ? '' : 'trnreg-required'" :rules="[birthFormatRule, birthDateRule]"
          :hint="birthFromYear ? t('trnreg.birth_date_from_year_hint') : (hasFideId ? t('trnreg.birth_date_optional_hint') : t('trnreg.birth_date_input_hint'))"
          persistent-hint
        ></v-text-field>
      </v-col>
      <slot name="contact" />
      <v-col cols="12" sm="4">
        <v-text-field v-model="p.national_id" :label="t('trnreg.field_national_id')" variant="outlined" color="green-darken-2" density="compact" :hint="t('trnreg.national_id_hint')" persistent-hint>
          <template #append-inner>
            <v-tooltip location="top" max-width="320">
              <template #activator="{ props: tip }">
                <v-icon v-bind="tip" size="small" color="grey-darken-1">mdi-information-outline</v-icon>
              </template>
              {{ t('trnreg.national_id_hint') }}
            </v-tooltip>
          </template>
        </v-text-field>
      </v-col>
      <v-col cols="12" sm="8">
        <v-autocomplete
          v-model="clubModel"
          :items="clubItems"
          item-title="title"
          item-value="value"
          :label="t('trnreg.field_club')"
          :hint="t('trnreg.club_hint')"
          persistent-hint
          clearable
          auto-select-first
          variant="outlined" color="green-darken-2" density="compact"
        ></v-autocomplete>
      </v-col>
      <!-- Shown, not ticked: facts about our records, read again on submit. -->
      <v-col cols="12" class="d-flex align-center ga-2 flex-wrap">
        <v-chip size="small" variant="tonal" :color="p.affiliated === true ? 'green-darken-2' : 'grey'">
          {{ t('trnreg.field_affiliated') }}: {{ yesNoUnknown(p.affiliated) }}
        </v-chip>
        <v-chip v-if="p.g_license" size="small" variant="tonal" color="blue-darken-2">{{ t('trnreg.field_g_license') }}</v-chip>
      </v-col>
      <v-col cols="12" sm="4">
        <v-text-field v-model="p.fide_id" :label="t('trnreg.field_fide_id')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
      </v-col>
      <v-col cols="12" sm="4">
        <v-select v-model="p.fide_title" :items="fideTitleItems" item-title="title" item-value="value" :label="t('trnreg.field_fide_title')" variant="outlined" color="green-darken-2" density="compact"></v-select>
      </v-col>
      <v-col cols="12" sm="4">
        <v-text-field :model-value="p.fide_federation" @update:model-value="(v) => (p.fide_federation = federationInput(v))" :label="t('trnreg.field_fide_federation')" :hint="t('trnreg.federation_hint')" placeholder="BEL" maxlength="3" :rules="[federationRule]" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
      </v-col>
      <v-col cols="12" v-if="needsFideIdWarning">
        <v-alert type="warning" variant="tonal" density="compact">{{ t('trnreg.fide_id_warning') }}</v-alert>
      </v-col>
      <!-- Only the rating this tournament is played for. -->
      <v-col cols="12" sm="4">
        <v-text-field
          v-model="p[ratingField]"
          v-digits
          :label="t('trnreg.' + ratingField.replace('fide_rating_', 'field_fide_rating_'))"
          :hint="ratingField !== 'fide_rating_standard' && !(Number(p[ratingField]) > 0) && Number(p.fide_rating_standard) > 0 ? t('trnreg.rating_fallback_hint') + ': ' + p.fide_rating_standard : ''"
          persistent-hint
          variant="outlined" color="green-darken-2" density="compact"
        ></v-text-field>
      </v-col>
      <v-col cols="12" sm="8">
        <!--
          0 or 1 category: nothing to choose, the box is locked. 2 or more:
          picked from the birth year when a category takes it, otherwise
          left blank and required.
        -->
        <v-select
          :model-value="p.category_index === '' ? null : p.category_index"
          @update:model-value="pickCategory"
          :items="categoryItems"
          :label="manyCategories ? req('trnreg.field_category') : t('trnreg.field_category')"
          :placeholder="t('trnreg.category_placeholder')"
          persistent-placeholder
          :hint="categoryAuto ? t('trnreg.category_auto_hint') : ''"
          persistent-hint
          variant="outlined" color="green-darken-2" density="compact"
          :disabled="!manyCategories"
          :class="manyCategories ? 'trnreg-required' : ''"
          :rules="manyCategories ? [requiredRule] : []"
        ></v-select>
      </v-col>
    </v-row>
  </div>
</template>

<style scoped>
.trnreg-required :deep(.v-label) {
  font-weight: 700;
}
.trnreg-search-first {
  background-color: #e8f5e9;
  border: 1px solid #a5d6a7;
}
.trnreg-lookup-wrap {
  position: relative;
}
.trnreg-dropdown {
  position: absolute;
  z-index: 20;
  top: 100%;
  left: 0;
  right: 0;
  margin: 0.15rem 0 0;
  padding: 0.25rem 0;
  list-style: none;
  background-color: rgb(var(--v-theme-surface));
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 0.375rem;
  box-shadow: 0 8px 20px rgba(27, 94, 32, 0.15);
  max-height: 240px;
  overflow-y: auto;
}
.trnreg-dropdown li {
  padding: 0.4rem 0.6rem;
  cursor: pointer;
  font-size: 0.9rem;
}
.trnreg-dropdown li:hover {
  background-color: #e8f5e9;
}
.trnreg-dropdown-meta {
  color: rgba(0, 0, 0, 0.6);
  font-size: 0.8rem;
  margin-left: 0.3rem;
}
.trnreg-searching-hint {
  display: block;
  font-size: 0.8rem;
  color: rgba(0, 0, 0, 0.6);
  margin-top: 0.15rem;
}
</style>

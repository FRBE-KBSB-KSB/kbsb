<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useI18n } from "vue-i18n"
import { storeToRefs } from "pinia"
import { useTournamentRegTokenStore } from "@/store/tournamentregtoken"

const { t, locale } = useI18n()
const route = useRoute()
const { $backend } = useNuxtApp()

const tokenStore = useTournamentRegTokenStore()
const { token } = storeToRefs(tokenStore)

definePageMeta({
  layout: "nomenu",
})

// ---------------------------------------------------------------------
// constants
// ---------------------------------------------------------------------

const EMPTY_REGISTRATION = {
  last_name: "",
  first_name: "",
  sex: "",
  date_birth: "",
  place_birth: "",
  country_residence: "",
  nationality: "",
  phone: "",
  gsm: "",
  email: "",
  national_id: "",
  national_club: "",
  national_club_name: "",
  affiliated: null,
  fide_id: "",
  fide_rating_standard: "",
  fide_rating_rapid: "",
  fide_rating_blitz: "",
  fide_title: "",
  fide_federation: "",
  category_index: "",
  note: "",
  contact: "",
  rounds_absent: "",
  g_license: false,
}

const EMPTY_TOURNAMENT = {
  name: "",
  address: "",
  city: "",
  system: "",
  rounds: "",
  categories: [],
  opening_registrations: "",
  closing_registrations: "",
  obligatory_presence: "",
  date_start: "",
  date_end: "",
  time_control: "",
  time_control_details: "",
  swar_cadence_number: "",
  event_code_fide_a: "",
  event_code_fide_b: "",
  event_code_fide_c: "",
  url: "",
  organizing_club: "",
  federation: "",
  chief_arbiter_person_id: "",
  chief_arbiter_name: "",
  chief_arbiter_email: "",
  chief_arbiter_phone: "",
  deputy_arbiter_1_person_id: "",
  deputy_arbiter_1_name: "",
  deputy_arbiter_1_email: "",
  deputy_arbiter_2_person_id: "",
  deputy_arbiter_2_name: "",
  deputy_arbiter_2_email: "",
  chief_organizer_person_id: "",
  chief_organizer_name: "",
  chief_organizer_email: "",
  chief_organizer_phone: "",
  email_copy_1: "",
  email_copy_2: "",
  email_copy_3: "",
  fide_homologated: false,
  export_per_category: false,
  // SWAR CSV export: line 17, [TIE_BREAK], [DATE], and line 12 per category.
  tiebreak_system: "",
  tiebreaks: [],
  round_dates: [],
  event_codes: [],
}

// SWAR's tie-break systems (line 17 of the CSV) and its numbered tie-breaks
// (_TB_01.._TB_16), in the order of the SWAR manual's list and its
// Prototype.csv. At most five, and only with the own-choice system.
const TIEBREAK_SYSTEMS = ["_TB_PERSONEL", "_TB_ELO_IRREGULIER", "_TB_ELO_REGULIER"]
const TIEBREAK_CODES = Array.from({ length: 16 }, (_, i) => i + 1)
const MAX_TIEBREAKS = 5

// What SWAR's CSV import accepts for categories (from its source): at most
// 16, of 32 characters each, and all numbers (ELO or age limits) or all
// names, never a mix. A round-robin takes only its own tie-break list.
const SWAR_MAX_CATEGORIES = 16
const SWAR_MAX_CATEGORY_LENGTH = 32
const ROBIN_SYSTEMS = ["ROBIN", "ROBIN_DBL", "ROBIN_AR"]
const numericCategory = (c) => /^-?\d+$/.test(String(c).trim()) && parseInt(c, 10) !== 0

// A choice list, and anything typed is kept too (the column holds up to 10
// characters).
const FEDERATION_OPTIONS = ["FIDE", "KBSB", "VSF", "FEFB", "SVDB"]

const SYSTEM_OPTIONS = [
  "SWISS", "SWISS_DBL", "SWISS_ACCELERE", "SWISS_321", "SWISS_BAKU",
  "SW_AMERICAIN", "SW_AMERICAIN_DBL", "ROBIN", "ROBIN_DBL", "ROBIN_AR",
]
const TIME_CONTROL_OPTIONS = ["Std", "Rapid", "Blitz"]

// swar_cadence_number is not free-form -- it's an index into one of three
// FIXED, per-time-control lookup tables of FIDE-homologated cadence
// descriptions, straight from the legacy tool's own cadences.php (still on
// the Z: full-site backup). "1" means something completely different under
// Std vs Rapid vs Blitz, which is why this is keyed by TIME_CONTROL_OPTIONS
// value and the picker below is gated on time_control being chosen first.
// Kept in the source language (French) -- these are the literal official
// cadence strings the legacy tool and SWAR both already use, not something
// this app translates.
const SWAR_CADENCES = {
  Std: [
    [1, "105 min/40 coups + 15 min. QPF"],
    [2, "120 min/40 coups + 15 min. avec incr. 30\" à partir du 40ème coup"],
    [3, "120 min/40 coups + 30 min. QPF"],
    [4, "120 min/10 coups + 30 min. avec incr. 30\" à partir du 40ème coup"],
    [5, "120 min QPF"],
    [6, "150 min QPF"],
    [7, "60 min QPF"],
    [8, "60 min avec incrément de 30\""],
    [9, "65 min QPF"],
    [10, "75 min avec incrément de 30\""],
    [11, "90 min/40 coups + 15 min avec incr. 30\" à partir du 1er coup"],
    [12, "90 min/40 coups + 30 min avec incr. 30\" à partir du 1er coup"],
    [13, "90 min avec incrément de 30\""],
    [14, "various - other"],
  ],
  Rapid: [
    [1, "10 min. avec incr. 10\""],
    [2, "10 min. avec incr. 15\""],
    [3, "10 min. avec incr. 5\""],
    [4, "11 min. QPF"],
    [5, "12 min. QPF"],
    [6, "13 min. avec incr. 3\""],
    [7, "13 min. avec incr. 5\""],
    [8, "15 min. QPF"],
    [9, "15 min. avec incr. 10\""],
    [10, "15 min. avec incr. 15\""],
    [11, "15 min. avec incr. 5\""],
    [12, "20 min. QPF"],
    [13, "20 min. avec incr. 10\""],
    [14, "20 min. avec incr. 15\""],
    [15, "20 min. avec incr. 5\""],
    [16, "25 min. QPF"],
    [17, "25 min. avec incr. 10\""],
    [18, "25 min. avec incr. 15\""],
    [19, "25 min. avec incr. 5\""],
    [20, "30 min. QPF"],
    [21, "45 min. QPF"],
    [22, "8 min. avec incr. 4\""],
    [23, "various - other"],
  ],
  Blitz: [
    [1, "3 min. avec incr. 2\""],
    [2, "3 min. avec incr. 3\""],
    [3, "4 min. avec incr. 2\""],
    [4, "4 min. avec incr. 3\""],
    [5, "5 min. QPF"],
    [6, "5 min. avec incr. 2\""],
    [7, "5 min. avec incr. 3\""],
    [8, "6 min. avec incr. 2\""],
    [9, "6 min. avec incr. 3\""],
    [10, "7 min. avec incr. 2\""],
    [11, "various - other"],
  ],
}

// ---------------------------------------------------------------------
// top-level view state
// ---------------------------------------------------------------------

// 'form' | 'list' | 'login' | 'admin'
//
// A tournament's own link, ?trn=X, opens on its list of players. Registering
// has its own address, ?trn=X&view=register, and a registration ends back on
// the list.
const view = ref("list")
const trnId = computed(() => route.query.trn || null)
const router = useRouter()

function setViewQuery(v) {
  if (!trnId.value) return
  const query = { ...route.query }
  if (v === "form") query.view = "register"
  else delete query.view
  router.replace({ query })
}

const tournament = ref(null)
const loadingTournament = ref(false)
const errorText = ref("")

const adminName = ref("")

function setLocale(l) {
  locale.value = l
}

function goToForm() {
  if (submittedRegistration.value) resetRegForm()
  view.value = "form"
  setViewQuery("form")
  if (!tournament.value) loadTournament()
}
function goToList() {
  view.value = "list"
  setViewQuery("list")
  loadRegistrations()
}
function goToLogin() {
  view.value = "login"
}
// From a tournament's own page (?trn=X) the dashboard opens on that
// tournament, not on the list of all of them.
async function goToAdmin() {
  view.value = "admin"
  if (!adminTournaments.value.length) await loadAdminTournaments()
  openAdminTournamentFromUrl()
}

function openAdminTournamentFromUrl() {
  if (!trnId.value) return
  const trn = adminTournaments.value.find((x) => String(x.id) === String(trnId.value))
  if (trn && (!selectedAdminTournament.value || selectedAdminTournament.value.id !== trn.id)) {
    selectAdminTournament(trn)
  }
}

function logout() {
  tokenStore.updateToken(null)
  adminName.value = ""
  if (typeof window !== "undefined") window.localStorage.removeItem("tournamentregname")
  selectedAdminTournament.value = null
  adminRegistrations.value = []
  adminTournaments.value = []
  view.value = trnId.value ? "list" : "login"
  if (trnId.value) loadRegistrations()
}

// ---------------------------------------------------------------------
// tournament header (public GET /:id)
// ---------------------------------------------------------------------

async function loadTournament() {
  if (!trnId.value) return
  loadingTournament.value = true
  errorText.value = ""
  try {
    const reply = await $backend("tournament_registrations", "getTournament", { id: trnId.value })
    tournament.value = reply.data.tournament
    applyCategoryDefault()
  } catch (error) {
    tournament.value = null
    errorText.value = error.code === 404 ? t("trnreg.tournament_not_found") : t("trnreg.load_tournament_failed")
  } finally {
    loadingTournament.value = false
  }
}

// A tournament with no categories, or exactly one, has nothing for a
// registrant to choose, so the box picks itself and is not editable: 0
// categories leaves it blank (there is nothing to pick), 1 selects that one
// index. Two or more leaves it blank and required, so a real choice has to
// be made rather than a default silently standing in for one.
function applyCategoryDefault() {
  const count = (tournament.value && Array.isArray(tournament.value.categories)) ? tournament.value.categories.length : 0
  regForm.value.category_index = count === 1 ? 0 : ""
}

// ---------------------------------------------------------------------
// player lookup (autocomplete-as-you-type), mirrors fide_registration.vue's
// searchOrganizer/selectOrganizer debounce pattern
// ---------------------------------------------------------------------

const lookupQuery = ref("")
const lookupResults = ref([])
const lookupSearching = ref(false)
const matchedBirthYear = ref(null)
let lookupTimer = null

function onLookupInput() {
  clearTimeout(lookupTimer)
  matchedBirthYear.value = null
  const q = lookupQuery.value
  if (!q || q.trim().length < 2) {
    lookupResults.value = []
    return
  }
  lookupTimer = setTimeout(async () => {
    lookupSearching.value = true
    try {
      const reply = await $backend("tournament_registrations", "lookup", { id: trnId.value, q })
      // a slower earlier keystroke can resolve after a later one; only apply
      // if the field still holds the query that triggered this request
      if (lookupQuery.value !== q) return
      lookupResults.value = (reply.data && reply.data.players) || []
    } catch (error) {
      if (lookupQuery.value === q) lookupResults.value = []
    } finally {
      if (lookupQuery.value === q) lookupSearching.value = false
    }
  }, 300)
}

// v-text-field type="number" still binds a string through v-model in
// Vuetify 3 -- convert the numeric-ish fields to real numbers (or null when
// blank) right before they go on the wire, so the backend doesn't receive
// "" where it expects an integer or null.
function cleanRegistrationPayload(form) {
  const payload = { ...form }
  // editRegForm is seeded from a full registration row (id, tournament_id,
  // created_at, updated_at, submitted_ip included) when opening the edit
  // dialog -- none of those are user-editable and tournament_id in
  // particular must never be re-sent as if it were part of the editable
  // body, so strip the non-writable fields regardless of which form (create
  // or edit) is being cleaned.
  delete payload.id
  delete payload.tournament_id
  delete payload.created_at
  delete payload.updated_at
  delete payload.submitted_ip
  ;["fide_rating_standard", "fide_rating_rapid", "fide_rating_blitz", "category_index"].forEach((k) => {
    const v = payload[k]
    payload[k] = v === "" || v === null || v === undefined ? null : Number(v)
  })
  return payload
}

function cleanTournamentPayload(form, obligatoryPresenceTimeValue, closingTimeValue) {
  const payload = { ...form }
  payload.closing_registrations = form.closing_registrations
    ? brusselsDateTimeToUtcIso(form.closing_registrations, closingTimeValue || DEFAULT_CLOSING_TIME)
    : ""
  payload.rounds = form.rounds === "" || form.rounds === null || form.rounds === undefined ? null : Number(form.rounds)
  // obligatory_presence is edited as a bare HH:MM (see obligatoryPresenceTime
  // below) and must be recombined with date_start into a full timestamp here
  // -- form.obligatory_presence may still hold a stale leftover value (e.g.
  // from spreading the original tournament row in openEditTournament), so
  // every branch below explicitly sets or removes it rather than letting
  // that leftover pass through untouched.
  if (!obligatoryPresenceTimeValue) {
    payload.obligatory_presence = ""
  } else if (form.date_start) {
    payload.obligatory_presence = brusselsDateTimeToUtcIso(form.date_start, obligatoryPresenceTimeValue)
  } else {
    delete payload.obligatory_presence
  }
  return payload
}

function applyLookupResult(target, p) {
  target.last_name = p.last_name || ""
  target.first_name = p.first_name || ""
  target.sex = p.sex || ""
  target.national_id = p.national_id || ""
  target.national_club = p.club || ""
  target.national_club_name = p.club_name || ""
  // Shown, not edited: the server reads both from our records on submit.
  target.affiliated = p.affiliated === true ? true : (p.affiliated === false ? false : null)
  target.g_license = p.g_license === true
  target.fide_id = p.fide_id || ""
  target.fide_rating_standard = p.fide_rating_standard || ""
  target.fide_rating_rapid = p.fide_rating_rapid || ""
  target.fide_rating_blitz = p.fide_rating_blitz || ""
  target.fide_title = p.fide_title || ""
  target.fide_federation = p.fide_federation || ""
  // players_national/players_fide have no "nationality" concept distinct
  // from federation -- fide_federation (e.g. "BEL") is the closest thing
  // lookup can supply, same substitution buildConfirmationEmail() already
  // makes for legacy's separate "Federation" field. Still a free-text
  // field the registrant can edit afterward, this only seeds it.
  target.nationality = p.fide_federation || ""
}

function selectLookupResult(p) {
  applyLookupResult(regForm.value, p)
  // Only birth_year is returned by lookup, not a full date -- date_birth
  // must stay whatever the registrant actually types, so just surface the
  // matched year as a hint instead of fabricating a fake day/month.
  matchedBirthYear.value = p.birth_year || null
  lookupQuery.value = p.name || `${p.first_name} ${p.last_name}`
  lookupResults.value = []
}

function hideLookupResults() {
  lookupResults.value = []
}

// ---------------------------------------------------------------------
// public registration form (create)
// ---------------------------------------------------------------------

const regForm = ref({ ...EMPTY_REGISTRATION })
const regFormRef = ref(null)
const regSubmitting = ref(false)
const regError = ref("")
const submittedRegistration = ref(null)

// Vuetify's `required` prop only draws the small asterisk; it does not by
// itself stop a submit. These rules are what actually enforces "mandatory"
// and "numbers and commas only", both for the inline red text under each
// field and for the hard stop in submitRegistration below.
const requiredRule = (v) => (v !== null && v !== undefined && String(v).trim() !== "") || t("trnreg.rule_required")

// A full birth date is only needed from somebody without a FIDE ID; the API
// applies the same rule.
const hasFideId = computed(() => String(regForm.value.fide_id || "").trim() !== "")
const birthDateRule = (v) => hasFideId.value || requiredRule(v)

// A FIDE-rated tournament, and this registrant has no FIDE ID yet.
const needsFideIdWarning = computed(() =>
  !!(tournament.value && tournament.value.fide_homologated) && !hasFideId.value
)

function yesNoUnknown(v) {
  if (v === true) return t("trnreg.yes")
  if (v === false) return t("trnreg.no")
  return "-"
}
const ROUNDS_ABSENT_RE = /^\s*\d+(\s*,\s*\d+)*\s*$/
const roundsAbsentRule = (v) => !v || ROUNDS_ABSENT_RE.test(v) || t("trnreg.rule_rounds_absent")

async function submitRegistration() {
  regError.value = ""
  const { valid } = await regFormRef.value.validate()
  if (!valid) {
    regError.value = t("trnreg.rule_required")
    return
  }
  regSubmitting.value = true
  // No standalone nationality box on this form any more; it is the same
  // concept as the FIDE federation box, so that is what gets stored under
  // it (mirrors applyLookupResult's own substitution for a match found by
  // the name lookup; this covers whoever typed the federation by hand
  // instead of picking a lookup result).
  regForm.value.nationality = regForm.value.fide_federation || ""
  try {
    const reply = await $backend("tournament_registrations", "createRegistration", {
      id: trnId.value,
      // Ephemeral -- only steers which language the confirmation email is
      // written in server-side (see buildConfirmationEmail() in
      // kbsb-dataplatform's routes/tournament_registrations.js); not a
      // registrations column, REGISTRATION_FIELDS ignores it.
      lang: locale.value,
      ...cleanRegistrationPayload(regForm.value),
    })
    submittedRegistration.value = reply.data.registration
    goToList()
    if (typeof window !== "undefined") window.scrollTo({ top: 0, behavior: "smooth" })
  } catch (error) {
    if (error.code === 409) {
      regError.value = t("trnreg.duplicate_error")
    } else if (error.errorCode === "registrations_not_open") {
      regError.value = t("trnreg.registrations_not_open_yet")
    } else if (error.errorCode === "registrations_closed") {
      regError.value = t("trnreg.registrations_closed")
    } else {
      regError.value = error.message || t("trnreg.submit_failed")
    }
  } finally {
    regSubmitting.value = false
  }
}

function resetRegForm() {
  regForm.value = { ...EMPTY_REGISTRATION }
  applyCategoryDefault()
  lookupQuery.value = ""
  lookupResults.value = []
  matchedBirthYear.value = null
  submittedRegistration.value = null
  regError.value = ""
}

// ---------------------------------------------------------------------
// public listing (GET /:id/registrations) + client-side filter/sort
// ---------------------------------------------------------------------

const registrations = ref([])
const loadingRegistrations = ref(false)
const listFilter = ref("")
const listSortKey = ref("rating")
const listSortOrder = ref("desc")

async function loadRegistrations() {
  if (!trnId.value) return
  loadingRegistrations.value = true
  errorText.value = ""
  try {
    const reply = await $backend("tournament_registrations", "getRegistrations", { id: trnId.value })
    registrations.value = (reply.data && reply.data.registrations) || []
  } catch (error) {
    errorText.value = error.message || t("trnreg.load_registrations_failed")
  } finally {
    loadingRegistrations.value = false
  }
}

// The rating that counts for a tournament: its own time control's, and for
// rapid or blitz the standard rating when the player has none in that one.
// Never blitz for a rapid tournament. FIDE writes 0 for "no rating".
const RATING_FIELD = { Std: "fide_rating_standard", Rapid: "fide_rating_rapid", Blitz: "fide_rating_blitz" }

function ratingField(trn) {
  return RATING_FIELD[trn && trn.time_control] || "fide_rating_standard"
}

function effectiveRating(r, trn) {
  const own = Number(r[ratingField(trn)])
  if (own > 0) return own
  const std = Number(r.fide_rating_standard)
  return std > 0 ? std : null
}

function sortCompare(a, b, key, mult, trn) {
  let valA = a[key]
  let valB = b[key]
  if (key === "rating") {
    valA = effectiveRating(a, trn) || 0
    valB = effectiveRating(b, trn) || 0
  } else if (key === "category_index" || key === "fide_rating_standard" || key === "id") {
    valA = Number(valA) || 0
    valB = Number(valB) || 0
  } else {
    valA = valA ? String(valA).toLowerCase() : ""
    valB = valB ? String(valB).toLowerCase() : ""
  }
  if (valA < valB) return -1 * mult
  if (valA > valB) return 1 * mult
  // Equal rating (including two unrated players): always break by name,
  // A-Z regardless of the rating column's own sort direction.
  if (key === "rating" || key === "fide_rating_standard") {
    const nameA = `${a.last_name || ""} ${a.first_name || ""}`.toLowerCase()
    const nameB = `${b.last_name || ""} ${b.first_name || ""}`.toLowerCase()
    if (nameA < nameB) return -1
    if (nameA > nameB) return 1
  }
  return 0
}

function matchesFilter(row, needle) {
  if (!needle) return true
  const hay = `${row.id} ${row.last_name} ${row.first_name} ${row.national_club} ${row.national_club_name} ${row.national_id}`.toLowerCase()
  return hay.includes(needle)
}

const filteredRegistrations = computed(() => {
  const needle = listFilter.value.trim().toLowerCase()
  return registrations.value.filter((r) => matchesFilter(r, needle))
})

const sortedRegistrations = computed(() => {
  const mult = listSortOrder.value === "asc" ? 1 : -1
  return [...filteredRegistrations.value].sort((a, b) => sortCompare(a, b, listSortKey.value, mult, tournament.value))
})

function toggleListSort(key) {
  if (listSortKey.value === key) {
    listSortOrder.value = listSortOrder.value === "asc" ? "desc" : "asc"
  } else {
    listSortKey.value = key
    listSortOrder.value = "asc"
  }
}

function categoryLabel(trn, index) {
  if (!trn || !Array.isArray(trn.categories)) return ""
  // Number(null) is 0 and Number("") is also 0 -- without this guard an
  // unset category_index would render as the FIRST category instead of
  // blank, since both null and 0 would coerce to the same index.
  if (index === null || index === undefined || index === "") return ""
  const i = Number(index)
  return Number.isInteger(i) && trn.categories[i] !== undefined ? trn.categories[i] : ""
}

// "Standaard: 90 min + 30 s" rather than the stored code "Std". The tempo
// itself is the details text the arbiter typed, or failing that the SWAR
// cadence they picked.
function tempoDisplay(trn) {
  if (!trn || !trn.time_control) return ""
  const name = t("trnreg.tc_" + trn.time_control)
  let tempo = (trn.time_control_details || "").trim()
  if (!tempo && trn.swar_cadence_number) {
    const row = (SWAR_CADENCES[trn.time_control] || []).find(([n]) => n === Number(trn.swar_cadence_number))
    if (row && !/^various/i.test(row[1])) tempo = row[1]
  }
  return tempo ? `${name}: ${tempo}` : name
}

function formatDateDisplay(iso) {
  if (!iso) return ""
  const m = String(iso).match(/^(\d{4})-(\d{2})-(\d{2})/)
  return m ? `${m[3]}/${m[2]}/${m[1]}` : String(iso)
}

// Postgres returns DATE/TIMESTAMPTZ columns as full ISO strings (e.g.
// "2026-05-01T00:00:00.000Z"), but <input type="date"> only accepts a bare
// "YYYY-MM-DD" and silently renders/resets to blank on anything else --
// without this, reopening an edit dialog shows the date boxes as empty even
// though the value is still in the database.
function toDateInputValue(iso) {
  if (!iso) return ""
  const m = String(iso).match(/^(\d{4}-\d{2}-\d{2})/)
  return m ? m[1] : ""
}

// ---------------------------------------------------------------------
// edit registration (shared dialog: public self-edit + admin-scoped edit)
// ---------------------------------------------------------------------

const editRegDialog = ref(false)
const editRegForm = ref({ ...EMPTY_REGISTRATION })
const editRegId = ref(null)
const editRegIsAdmin = ref(false)
const editRegSubmitting = ref(false)
const editRegError = ref("")
const editRegLookupQuery = ref("")
const editRegLookupResults = ref([])
const editRegLookupSearching = ref(false)
let editRegLookupTimer = null

// Admin only, as of 2026-09-22: this used to also open for anyone reading
// the public list, with no login of any kind beyond knowing a registration's
// numeric id (sequential, visible in that same list) -- a "Wijzigen" button
// letting any visitor rewrite any other registrant's details. Removed here
// together with the button that reached it and the public write endpoint on
// the Node side (see kbsb-dataplatform's routes/tournament_registrations.js).
// `row` comes from admin_getRegistrations, already full-fidelity and
// authenticated, so it is used as-is; there is no longer a second, public
// path that re-fetches a single row by id.
function openEditRegistration(row) {
  editRegId.value = row.id
  editRegIsAdmin.value = true
  editRegLookupQuery.value = ""
  editRegLookupResults.value = []
  editRegError.value = ""
  editRegForm.value = { ...EMPTY_REGISTRATION, ...row, date_birth: toDateInputValue(row.date_birth) }
  editRegDialog.value = true
}

function closeEditRegistration() {
  editRegDialog.value = false
}

function onEditRegLookupInput() {
  clearTimeout(editRegLookupTimer)
  const q = editRegLookupQuery.value
  const lookupTournamentId = editRegIsAdmin.value ? (selectedAdminTournament.value && selectedAdminTournament.value.id) : trnId.value
  if (!q || q.trim().length < 2) {
    editRegLookupResults.value = []
    return
  }
  editRegLookupTimer = setTimeout(async () => {
    editRegLookupSearching.value = true
    try {
      const reply = await $backend("tournament_registrations", "lookup", { id: lookupTournamentId, q })
      if (editRegLookupQuery.value !== q) return
      editRegLookupResults.value = (reply.data && reply.data.players) || []
    } catch (error) {
      if (editRegLookupQuery.value === q) editRegLookupResults.value = []
    } finally {
      if (editRegLookupQuery.value === q) editRegLookupSearching.value = false
    }
  }, 300)
}

function selectEditRegLookupResult(p) {
  applyLookupResult(editRegForm.value, p)
  editRegLookupQuery.value = p.name || `${p.first_name} ${p.last_name}`
  editRegLookupResults.value = []
}

const editRegCategories = computed(() => {
  const trn = editRegIsAdmin.value ? selectedAdminTournament.value : tournament.value
  return (trn && trn.categories) || []
})

async function saveEditRegistration() {
  editRegSubmitting.value = true
  editRegError.value = ""
  try {
    await $backend("tournament_registrations", "admin_updateRegistration", {
      id: editRegId.value,
      token: token.value,
      ...cleanRegistrationPayload(editRegForm.value),
    })
    editRegDialog.value = false
    await loadAdminRegistrations()
  } catch (error) {
    if (error.code === 409) editRegError.value = t("trnreg.duplicate_error")
    else if (error.code === 404) editRegError.value = t("trnreg.registration_not_found")
    else editRegError.value = error.message || t("trnreg.update_failed")
  } finally {
    editRegSubmitting.value = false
  }
}

async function deleteRegistration(row) {
  if (typeof window !== "undefined" && !window.confirm(t("trnreg.delete_confirm"))) return
  adminActionError.value = ""
  adminActionNotice.value = ""
  try {
    await $backend("tournament_registrations", "admin_deleteRegistration", { id: row.id, token: token.value })
    adminActionNotice.value = t("trnreg.delete_success")
    await loadAdminRegistrations()
  } catch (error) {
    adminActionError.value = error.message || t("trnreg.delete_failed")
  }
}

// ---------------------------------------------------------------------
// admin login
// ---------------------------------------------------------------------

const loginUsername = ref("")
const loginPassword = ref("")
const loginError = ref("")
const loginSubmitting = ref(false)

// Any KBSB member with an Odoo account can log in and run their own
// tournaments; the password logins below are the older arbiter accounts. Both
// end in the same kind of session, and both see only their own tournaments.
const odooEmail = ref("")
const odooPassword = ref("")
const showPasswordLogin = ref(false)

async function startAdminSession(reply) {
  tokenStore.updateToken(reply.data.token)
  adminName.value = reply.data.name || ""
  if (typeof window !== "undefined") window.localStorage.setItem("tournamentregname", adminName.value)
  view.value = "admin"
  await loadAdminTournaments()
  openAdminTournamentFromUrl()
}

async function submitOdooLogin() {
  loginSubmitting.value = true
  loginError.value = ""
  try {
    const reply = await $backend("tournament_registrations", "admin_odooLogin", {
      email: odooEmail.value,
      password: odooPassword.value,
    })
    odooPassword.value = ""
    await startAdminSession(reply)
  } catch (error) {
    if (error.code === 401) loginError.value = t("trnreg.login_failed")
    else if (error.code === 403) loginError.value = t("trnreg.odoo_not_member")
    else loginError.value = error.message || t("trnreg.login_failed")
  } finally {
    loginSubmitting.value = false
  }
}

async function submitLogin() {
  loginSubmitting.value = true
  loginError.value = ""
  try {
    const reply = await $backend("tournament_registrations", "admin_login", {
      username: loginUsername.value,
      password: loginPassword.value,
    })
    tokenStore.updateToken(reply.data.token)
    adminName.value = reply.data.name || ""
    if (typeof window !== "undefined") window.localStorage.setItem("tournamentregname", adminName.value)
    loginPassword.value = ""
    view.value = "admin"
    await loadAdminTournaments()
    openAdminTournamentFromUrl()
  } catch (error) {
    loginError.value = error.code === 401 ? t("trnreg.login_failed") : (error.message || t("trnreg.login_failed"))
  } finally {
    loginSubmitting.value = false
  }
}

// ---------------------------------------------------------------------
// admin dashboard: my tournaments
// ---------------------------------------------------------------------

const adminTournaments = ref([])
const loadingAdminTournaments = ref(false)
const adminActionError = ref("")
const adminActionNotice = ref("")

const selectedAdminTournament = ref(null)
const adminRegistrations = ref([])
const loadingAdminRegistrations = ref(false)
const adminListSortKey = ref("id")
const adminListSortOrder = ref("asc")

const sortedAdminRegistrations = computed(() => {
  const mult = adminListSortOrder.value === "asc" ? 1 : -1
  return [...adminRegistrations.value].sort((a, b) => sortCompare(a, b, adminListSortKey.value, mult, selectedAdminTournament.value))
})

function toggleAdminListSort(key) {
  if (adminListSortKey.value === key) {
    adminListSortOrder.value = adminListSortOrder.value === "asc" ? "desc" : "asc"
  } else {
    adminListSortKey.value = key
    adminListSortOrder.value = "asc"
  }
}

async function loadAdminTournaments() {
  if (!token.value) return
  loadingAdminTournaments.value = true
  adminActionError.value = ""
  try {
    const reply = await $backend("tournament_registrations", "admin_getMyTournaments", { token: token.value })
    adminTournaments.value = (reply.data && reply.data.tournaments) || []
    myOwner.value = (reply.data && reply.data.owner) || null
  } catch (error) {
    adminActionError.value = error.message || t("trnreg.admin_load_tournaments_failed")
    if (error.code === 401) logout()
  } finally {
    loadingAdminTournaments.value = false
  }
}

function selectAdminTournament(trn) {
  selectedAdminTournament.value = trn
  refreshEloResult.value = null
  adminActionError.value = ""
  adminActionNotice.value = ""
  loadAdminRegistrations()
  loadTournamentAdmins()
}

// ---------------------------------------------------------------------
// admin: sharing a tournament with other admins, by member number
// ---------------------------------------------------------------------

// Who is logged in, as the API identifies owners, so a tournament shared
// with me can be told from one of my own.
const myOwner = ref(null)
const tournamentAdmins = ref([])
const newAdminNationalId = ref("")
const adminsBusy = ref(false)
const adminsError = ref("")

function isMine(trn) {
  return !!trn && trn.owner === myOwner.value
}

async function loadTournamentAdmins() {
  tournamentAdmins.value = []
  adminsError.value = ""
  if (!selectedAdminTournament.value) return
  try {
    const reply = await $backend("tournament_registrations", "admin_getTournamentAdmins", {
      id: selectedAdminTournament.value.id,
      token: token.value,
    })
    tournamentAdmins.value = reply.data.admins || []
  } catch (error) {
    adminsError.value = error.message
  }
}

async function addTournamentAdmin() {
  const id = String(newAdminNationalId.value || "").trim()
  if (!/^-?\d+$/.test(id)) {
    adminsError.value = t("trnreg.share_need_number")
    return
  }
  adminsBusy.value = true
  adminsError.value = ""
  try {
    const reply = await $backend("tournament_registrations", "admin_addTournamentAdmin", {
      id: selectedAdminTournament.value.id,
      token: token.value,
      national_id: Number(id),
    })
    tournamentAdmins.value = reply.data.admins || []
    newAdminNationalId.value = ""
  } catch (error) {
    adminsError.value = error.code === 404 ? t("trnreg.share_no_member").replace("{id}", id) : error.message
  } finally {
    adminsBusy.value = false
  }
}

async function removeTournamentAdmin(admin) {
  const label = admin.name ? `${admin.name} (${admin.national_id})` : String(admin.national_id)
  if (typeof window !== "undefined" && !window.confirm(t("trnreg.share_remove_confirm").replace("{who}", label))) return
  adminsBusy.value = true
  adminsError.value = ""
  try {
    const reply = await $backend("tournament_registrations", "admin_removeTournamentAdmin", {
      id: selectedAdminTournament.value.id,
      token: token.value,
      national_id: admin.national_id,
    })
    tournamentAdmins.value = reply.data.admins || []
  } catch (error) {
    adminsError.value = error.message
  } finally {
    adminsBusy.value = false
  }
}

function backToTournamentList() {
  selectedAdminTournament.value = null
  adminRegistrations.value = []
}

// ---------------------------------------------------------------------
// admin: delete tournament (type-the-name confirmation)
// ---------------------------------------------------------------------

const deleteTournamentDialog = ref(false)
const deleteTournamentTarget = ref(null)
const deleteTournamentConfirmText = ref("")
const deleteTournamentSubmitting = ref(false)
const deleteTournamentError = ref("")

// Requires typing the tournament's own NAME back, not just a generic word
// like "DELETE" -- this cascades to every one of its registrations (real
// player data, see the schema's ON DELETE CASCADE), and the admin dashboard
// can have several tournaments open/visible at once, so forcing the name
// forces actually reading which one is about to go, not just reflexively
// confirming a dialog.
function openDeleteTournament(trn) {
  deleteTournamentTarget.value = trn
  deleteTournamentConfirmText.value = ""
  deleteTournamentError.value = ""
  deleteTournamentDialog.value = true
}

function closeDeleteTournament() {
  deleteTournamentDialog.value = false
  deleteTournamentTarget.value = null
}

async function confirmDeleteTournament() {
  if (!deleteTournamentTarget.value || deleteTournamentConfirmText.value !== deleteTournamentTarget.value.name) return
  deleteTournamentSubmitting.value = true
  deleteTournamentError.value = ""
  try {
    await $backend("tournament_registrations", "admin_deleteTournament", { id: deleteTournamentTarget.value.id, token: token.value })
    const wasSelected = selectedAdminTournament.value && selectedAdminTournament.value.id === deleteTournamentTarget.value.id
    deleteTournamentDialog.value = false
    deleteTournamentTarget.value = null
    if (wasSelected) backToTournamentList()
    adminActionNotice.value = t("trnreg.admin_delete_tournament_success")
    await loadAdminTournaments()
  } catch (error) {
    deleteTournamentError.value = error.message || t("trnreg.admin_delete_tournament_failed")
  } finally {
    deleteTournamentSubmitting.value = false
  }
}

// Same route, ?trn=<id> only -- lands on the page's default (form) view for
// that tournament, i.e. what a registrant would see. Opened with window.open
// so the admin's own dashboard/session in this tab is undisturbed.
//
// The page's own fixed address rather than route.path, which is wherever the
// dashboard happens to be showing (a trailing slash there is a 404 on App
// Engine), and a real link rather than window.open, which a browser may
// block or open blank.
const PUBLIC_PAGE_PATH = "/tools/tournament_registrations"

function publicTournamentUrl(trn) {
  return `${PUBLIC_PAGE_PATH}?trn=${encodeURIComponent(trn.id)}`
}

async function loadAdminRegistrations() {
  if (!selectedAdminTournament.value) return
  loadingAdminRegistrations.value = true
  try {
    const reply = await $backend("tournament_registrations", "admin_getRegistrations", { id: selectedAdminTournament.value.id, token: token.value })
    adminRegistrations.value = (reply.data && reply.data.registrations) || []
  } catch (error) {
    adminActionError.value = error.message || t("trnreg.load_registrations_failed")
  } finally {
    loadingAdminRegistrations.value = false
  }
}

// ---------------------------------------------------------------------
// admin: create / edit tournament
// ---------------------------------------------------------------------

const tournamentFormDialog = ref(false)
const tournamentFormMode = ref("create")
const tournamentForm = ref({ ...EMPTY_TOURNAMENT })
const tournamentSubmitting = ref(false)
const tournamentFormError = ref("")

const cadenceOptions = computed(() => {
  const table = SWAR_CADENCES[tournamentForm.value.time_control]
  if (!table) return []
  return table.map(([num, desc]) => ({ title: `${num} — ${desc}`, value: num }))
})

// obligatory_presence is a full timestamp in the data model, but it has only
// ever meant "what time on the tournament's own date_start" -- the date
// component is always redundant with date_start. The UI captures just the
// HH:MM here; saveTournament()/cleanTournamentPayload() recombine it with
// tournamentForm.value.date_start right before the request goes out. Kept as
// its own ref (not bound directly to tournamentForm.obligatory_presence)
// because an <input type="time"> needs a bare "HH:MM" string, not a
// timestamp.
const obligatoryPresenceTime = ref("")

// Every time on this page is Brussels time: the tournaments are played in
// Belgium. Reading the inputs in the browser's own timezone is how an arbiter
// in Uzbekistan typed 13:45 and players were mailed 10:45. So the date and
// time typed are taken as Brussels wall-clock time and turned into a UTC
// instant here, and shown back the same way, wherever the browser is.
const BRUSSELS_PARTS = new Intl.DateTimeFormat("en-GB", {
  timeZone: "Europe/Brussels",
  hourCycle: "h23",
  year: "numeric", month: "2-digit", day: "2-digit",
  hour: "2-digit", minute: "2-digit", second: "2-digit",
})

function brusselsFields(ts) {
  const p = {}
  for (const part of BRUSSELS_PARTS.formatToParts(new Date(ts))) p[part.type] = part.value
  return p
}

// How far Brussels wall-clock time is ahead of UTC at this instant, in ms.
function brusselsOffsetMs(ts) {
  const p = brusselsFields(ts)
  const wall = Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour, +p.minute, +p.second)
  return wall - Math.floor(ts / 1000) * 1000
}

function brusselsDateTimeToUtcIso(dateStr, timeStr) {
  const [y, mo, d] = dateStr.split("-").map(Number)
  const [h, mi] = timeStr.split(":").map(Number)
  const wall = Date.UTC(y, mo - 1, d, h, mi, 0)
  // Twice, so an instant on the other side of a DST change settles on the
  // offset that applies at the result rather than at the first guess.
  let ts = wall - brusselsOffsetMs(wall)
  ts = wall - brusselsOffsetMs(ts)
  return new Date(ts).toISOString()
}

// A stored UTC instant as the Brussels date ("YYYY-MM-DD") and time ("HH:MM").
function brusselsParts(value) {
  if (!value) return { date: "", time: "" }
  const dt = new Date(value)
  if (isNaN(dt.getTime())) return { date: "", time: "" }
  const p = brusselsFields(dt.getTime())
  return { date: `${p.year}-${p.month}-${p.day}`, time: `${p.hour}:${p.minute}` }
}

function utcIsoToBrusselsHHMM(value) {
  return brusselsParts(value).time
}

// Closing of registrations is a date and a time: from that minute on, the
// public form is replaced by a notice and the API refuses submissions (see
// registrationsClosed() in kbsb-dataplatform's tournament_registrations.js,
// which applies the same rule). 23:59 unless the arbiter picks otherwise.
const DEFAULT_CLOSING_TIME = "23:59"
const closingTime = ref(DEFAULT_CLOSING_TIME)

// Closings saved before the time existed went in as a bare date, stored as
// exactly midnight UTC; they still mean "open through that whole day".
function isDateOnlyInstant(value) {
  const dt = new Date(value)
  return (
    dt.getUTCHours() === 0 && dt.getUTCMinutes() === 0 &&
    dt.getUTCSeconds() === 0 && dt.getUTCMilliseconds() === 0
  )
}

// A stored closing instant as the date and time the form edits.
function closingParts(value) {
  if (!value) return { date: "", time: DEFAULT_CLOSING_TIME }
  const dt = new Date(value)
  if (isNaN(dt.getTime())) return { date: "", time: DEFAULT_CLOSING_TIME }
  if (isDateOnlyInstant(value)) return { date: toDateInputValue(value), time: DEFAULT_CLOSING_TIME }
  return brusselsParts(value)
}

function closingDisplay(value) {
  const { date, time } = closingParts(value)
  return date ? `${formatDateDisplay(date)} ${time}` : ""
}

function registrationsClosedAt(value, now = new Date()) {
  if (!value) return false
  const dt = new Date(value)
  if (isNaN(dt.getTime())) return false
  if (isDateOnlyInstant(value)) {
    const today = new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Brussels" }).format(now)
    return today > toDateInputValue(value)
  }
  return now.getTime() >= dt.getTime()
}

// Re-read every 30 seconds, so a page left open across the closing time
// swaps the form for the notice instead of letting somebody fill it in for
// nothing.
const nowTick = ref(Date.now())
let nowTimer = null
onMounted(() => {
  nowTimer = setInterval(() => (nowTick.value = Date.now()), 30000)
})
onBeforeUnmount(() => clearInterval(nowTimer))

const registrationsClosed = computed(() =>
  registrationsClosedAt(tournament.value && tournament.value.closing_registrations, new Date(nowTick.value))
)

// ---- arbiter/organizer lookup, mirrors the player lookup near the top of
// this file but keyed by slot since there are 4 independent person pickers
// in the tournament form (chief_arbiter, deputy_arbiter_1, deputy_arbiter_2,
// chief_organizer) ----

const ARBITER_SLOTS = ["chief_arbiter", "deputy_arbiter_1", "deputy_arbiter_2", "chief_organizer"]

function emptyArbiterLookupState() {
  const state = {}
  ARBITER_SLOTS.forEach((slot) => {
    state[slot] = { query: "", results: [], searching: false }
  })
  return state
}

const arbiterLookup = ref(emptyArbiterLookupState())
const arbiterLookupTimers = {}

function resetArbiterLookupState() {
  arbiterLookup.value = emptyArbiterLookupState()
}

function onArbiterLookupInput(slot) {
  clearTimeout(arbiterLookupTimers[slot])
  const q = arbiterLookup.value[slot].query
  if (!q || q.trim().length < 2) {
    arbiterLookup.value[slot].results = []
    return
  }
  arbiterLookupTimers[slot] = setTimeout(async () => {
    arbiterLookup.value[slot].searching = true
    try {
      const reply = await $backend("tournament_registrations", "lookupGlobal", { q })
      // a slower earlier keystroke can resolve after a later one; only apply
      // if the field still holds the query that triggered this request
      if (arbiterLookup.value[slot].query !== q) return
      arbiterLookup.value[slot].results = (reply.data && reply.data.players) || []
    } catch (error) {
      if (arbiterLookup.value[slot].query === q) arbiterLookup.value[slot].results = []
    } finally {
      if (arbiterLookup.value[slot].query === q) arbiterLookup.value[slot].searching = false
    }
  }, 300)
}

// Critical: person_id for these 4 slots is sourced from fide_id, NOT
// national_id -- this matches the legacy tool's own schema comment for e.g.
// chief_arbiter_id ("Fide-ID Arbitre principal"). If the selected person has
// no fide_id, leave person_id blank rather than silently falling back to a
// different kind of id.
function selectArbiterLookupResult(slot, person) {
  const name = person.name || `${person.first_name} ${person.last_name}`
  tournamentForm.value[`${slot}_person_id`] = person.fide_id || ""
  tournamentForm.value[`${slot}_name`] = name
  // Fill the search box with the picked name instead of clearing it -- the
  // old behavior blanked the box and relied entirely on the separate
  // "Selected: NAME" line below to show what got picked, inconsistent with
  // the registration form's own selectLookupResult(), which fills its query
  // box the same way. Read as "the box went empty, did my pick not work?"
  arbiterLookup.value[slot].query = name
  arbiterLookup.value[slot].results = []
}

function clearArbiterSelection(slot) {
  tournamentForm.value[`${slot}_person_id`] = ""
  tournamentForm.value[`${slot}_name`] = ""
}

function hideArbiterLookupResults(slot) {
  arbiterLookup.value[slot].results = []
}

function openNewTournament() {
  tournamentFormMode.value = "create"
  tournamentForm.value = { ...EMPTY_TOURNAMENT, categories: [], tiebreaks: [], round_dates: [], event_codes: [] }
  obligatoryPresenceTime.value = ""
  closingTime.value = DEFAULT_CLOSING_TIME
  resetArbiterLookupState()
  tournamentFormError.value = ""
  tournamentFormDialog.value = true
}

function openEditTournament(trn) {
  tournamentFormMode.value = "edit"
  tournamentForm.value = {
    ...EMPTY_TOURNAMENT,
    ...trn,
    categories: Array.isArray(trn.categories) ? [...trn.categories] : [],
    date_start: toDateInputValue(trn.date_start),
    date_end: toDateInputValue(trn.date_end),
    opening_registrations: toDateInputValue(trn.opening_registrations),
    closing_registrations: closingParts(trn.closing_registrations).date,
    tiebreak_system: trn.tiebreak_system || "",
    tiebreaks: Array.isArray(trn.tiebreaks) ? [...trn.tiebreaks] : [],
    round_dates: Array.isArray(trn.round_dates) ? trn.round_dates.map(toDateInputValue) : [],
    // The old A/B/C boxes, for a tournament saved before the list existed.
    event_codes: Array.isArray(trn.event_codes) && trn.event_codes.length
      ? [...trn.event_codes]
      : [trn.event_code_fide_a, trn.event_code_fide_b, trn.event_code_fide_c].map((c) => c || ""),
  }
  obligatoryPresenceTime.value = utcIsoToBrusselsHHMM(trn.obligatory_presence)
  closingTime.value = closingParts(trn.closing_registrations).time
  // trn already carries <slot>_person_id/_name from the API -- those show up
  // as the "currently selected" person for each slot (the template reads
  // them straight off tournamentForm) without forcing a fresh lookup. Only
  // the search boxes themselves get reset here; a value is only replaced if
  // the admin actively searches and picks a result (selectArbiterLookupResult)
  // or clears it (clearArbiterSelection).
  resetArbiterLookupState()
  tournamentFormError.value = ""
  tournamentFormDialog.value = true
}

function closeTournamentForm() {
  tournamentFormDialog.value = false
}

// A new tournament with every setting of this one, and none of its
// registrations. Saving creates it; nothing is written before that.
function openCopyTournament(trn) {
  openEditTournament(trn)
  tournamentFormMode.value = "create"
  delete tournamentForm.value.id
  delete tournamentForm.value.created_at
  delete tournamentForm.value.updated_at
  tournamentForm.value.name = `${trn.name || ""} ${t("trnreg.copy_suffix")}`.trim()
}

function fillOrganizerFromChiefArbiter() {
  const f = tournamentForm.value
  f.chief_organizer_person_id = f.chief_arbiter_person_id
  f.chief_organizer_name = f.chief_arbiter_name
  f.chief_organizer_email = f.chief_arbiter_email
  f.chief_organizer_phone = f.chief_arbiter_phone
  arbiterLookup.value.chief_organizer.query = f.chief_arbiter_name || ""
}

// A date box that is still empty starts on its partner's date, so the
// picker opens on that month rather than on today: the end date on the
// start date, the closing of registrations on their opening.
function prefillFrom(target, source) {
  const f = tournamentForm.value
  if (!f[target] && f[source]) f[target] = f[source]
}

// The same checks the API makes, so the arbiter sees them before saving.
function tournamentFormProblem() {
  const f = tournamentForm.value
  if (f.date_start && f.date_end && f.date_end < f.date_start) return t("trnreg.rule_end_after_start")
  if (f.opening_registrations && f.closing_registrations && f.closing_registrations < f.opening_registrations) {
    return t("trnreg.rule_closing_after_opening")
  }
  // Registrations close no later than the tournament starts: not after its
  // first day, and on that day not after the obligatory presence time.
  if (f.closing_registrations && f.date_start) {
    if (f.closing_registrations > f.date_start) return t("trnreg.rule_closing_before_start")
    if (f.closing_registrations === f.date_start && obligatoryPresenceTime.value &&
        (closingTime.value || DEFAULT_CLOSING_TIME) > obligatoryPresenceTime.value) {
      return t("trnreg.rule_closing_before_presence")
    }
  }
  const codes = eventCodeSlots.value.map((_, i) => String(f.event_codes[i] || "").trim())
  if (codes.some((c) => c && !/^\d{1,12}$/.test(c))) return t("trnreg.rule_event_code_number")
  if (f.fide_homologated && !codes.some((c) => c)) return t("trnreg.rule_event_code_required")
  if (ROBIN_SYSTEMS.includes(f.system) && f.tiebreak_system && f.tiebreak_system !== "_TB_PERSONEL") {
    return t("trnreg.rule_robin_tiebreaks")
  }
  const cats = (f.categories || []).filter((c) => c && c.trim())
  if (cats.length > SWAR_MAX_CATEGORIES) return t("trnreg.rule_categories_max")
  if (cats.some((c) => c.trim().length > SWAR_MAX_CATEGORY_LENGTH)) return t("trnreg.rule_category_length")
  if (cats.some((c) => c.includes(";"))) return t("trnreg.rule_category_semicolon")
  if (cats.some(numericCategory) && !cats.every(numericCategory)) return t("trnreg.rule_categories_mixed")
  if (f.tiebreak_system === "_TB_PERSONEL") {
    const picked = f.tiebreaks.filter((n) => n)
    if (new Set(picked).size !== picked.length) return t("trnreg.rule_tiebreak_twice")
  }
  // SWAR wants one date per round or none at all.
  const dates = roundDateSlots.value.map((_, i) => f.round_dates[i] || "")
  if (dates.some((d) => d)) {
    if (dates.some((d) => !d)) return t("trnreg.rule_round_dates_all")
    for (let i = 1; i < dates.length; i++) {
      if (dates[i] < dates[i - 1]) return t("trnreg.rule_round_dates_order")
    }
    if ((f.date_start && dates[0] < f.date_start) || (dates[dates.length - 1] > (f.date_end || f.date_start || "9999"))) {
      return t("trnreg.rule_round_dates_inside")
    }
  }
  return ""
}

// One FIDE event code per category when the tournament exports per category
// (each category is then its own SWAR tournament and FIDE event), otherwise
// one for the whole tournament.
const eventCodeSlots = computed(() => {
  const f = tournamentForm.value
  const named = (f.categories || []).filter((c) => c && c.trim())
  return f.export_per_category && named.length >= 2 ? named : [""]
})

// A date box per round, once the number of rounds is known.
const roundDateSlots = computed(() => {
  const n = Number(tournamentForm.value.rounds)
  return Number.isInteger(n) && n > 0 && n <= 60 ? Array.from({ length: n }, (_, i) => i + 1) : []
})

// Consecutive days from the first round's date (or the start date), a
// starting point to correct rather than type 9 dates by hand.
function fillRoundDatesDaily() {
  const f = tournamentForm.value
  const first = f.round_dates[0] || f.date_start
  if (!first) return
  const [y, m, d] = first.split("-").map(Number)
  f.round_dates = roundDateSlots.value.map((_, i) => {
    const dt = new Date(Date.UTC(y, m - 1, d + i))
    return dt.toISOString().slice(0, 10)
  })
}

function addTiebreakRow() {
  if (tournamentForm.value.tiebreaks.length < MAX_TIEBREAKS) tournamentForm.value.tiebreaks.push(null)
}
function removeTiebreakRow(i) {
  tournamentForm.value.tiebreaks.splice(i, 1)
}

// The SWAR fields as the API wants them: only what is filled in, sized to the
// rounds and categories actually there.
function swarPayload(f) {
  const codes = eventCodeSlots.value.map((_, i) => String(f.event_codes[i] || "").trim())
  const dates = roundDateSlots.value.map((_, i) => f.round_dates[i] || "")
  return {
    tiebreak_system: f.tiebreak_system || "",
    tiebreaks: f.tiebreak_system === "_TB_PERSONEL" ? f.tiebreaks.filter((n) => n).map(Number) : [],
    round_dates: dates.every((d) => d) ? dates : [],
    event_codes: codes.some((c) => c) ? codes : [],
    // Kept in step, so an older reader of the A/B/C columns never sees a code
    // that was removed here.
    event_code_fide_a: codes[0] || "",
    event_code_fide_b: codes[1] || "",
    event_code_fide_c: codes[2] || "",
  }
}

// A tournament is archived from the day after its last day (Brussels), and
// leaves the working list for a collapsed archive below it.
const showArchived = ref(false)

function tournamentArchived(trn) {
  const last = toDateInputValue(trn.date_end) || toDateInputValue(trn.date_start)
  if (!last) return false
  const today = new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Brussels" }).format(new Date(nowTick.value))
  return today > last
}

const activeAdminTournaments = computed(() => adminTournaments.value.filter((trn) => !tournamentArchived(trn)))
const archivedAdminTournaments = computed(() => adminTournaments.value.filter((trn) => tournamentArchived(trn)))

function addCategoryRow() {
  tournamentForm.value.categories.push("")
}
function removeCategoryRow(i) {
  tournamentForm.value.categories.splice(i, 1)
}

async function saveTournament() {
  tournamentFormError.value = tournamentFormProblem()
  if (tournamentFormError.value) return
  tournamentSubmitting.value = true
  adminActionNotice.value = ""
  try {
    const categories = tournamentForm.value.categories.filter((c) => c && c.trim())
    const payload = {
      ...cleanTournamentPayload(tournamentForm.value, obligatoryPresenceTime.value, closingTime.value),
      categories,
      ...swarPayload(tournamentForm.value),
    }
    delete payload.id
    delete payload.created_at
    delete payload.updated_at
    let reply
    if (tournamentFormMode.value === "create") {
      reply = await $backend("tournament_registrations", "admin_createTournament", { token: token.value, ...payload })
    } else {
      reply = await $backend("tournament_registrations", "admin_updateTournament", {
        id: tournamentForm.value.id,
        token: token.value,
        ...payload,
      })
    }
    tournamentFormDialog.value = false
    adminActionNotice.value = t("trnreg.admin_save_tournament_success")
    await loadAdminTournaments()
    if (reply.data && reply.data.tournament && selectedAdminTournament.value && selectedAdminTournament.value.id === reply.data.tournament.id) {
      selectedAdminTournament.value = reply.data.tournament
    }
  } catch (error) {
    tournamentFormError.value = error.message || t("trnreg.admin_save_tournament_failed")
  } finally {
    tournamentSubmitting.value = false
  }
}

// ---------------------------------------------------------------------
// admin: CSV / SWAR exports + ELO refresh
// ---------------------------------------------------------------------

// Keyed "all" or the category number, so each button spins on its own.
const exportingCsv = ref({})
const exportingSwar = ref({})

// One button per category when the tournament exports per category, and a
// single one for everything otherwise (or when it has at most one category).
const exportTargets = computed(() => {
  const trn = selectedAdminTournament.value
  const cats = (trn && Array.isArray(trn.categories)) ? trn.categories : []
  if (!trn || !trn.export_per_category || cats.length < 2) return [{ key: "all", label: "" }]
  return cats.map((c, i) => ({ key: String(i), label: c }))
})
const refreshEloLoading = ref(false)
const refreshEloResult = ref(null)

function triggerDownload(blob, filename) {
  const downloadUrl = window.URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = downloadUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(downloadUrl)
}

function exportFileTag(key) {
  return key === "all" ? "" : `_cat${Number(key) + 1}`
}

async function exportCsv(key) {
  if (!selectedAdminTournament.value) return
  exportingCsv.value = { ...exportingCsv.value, [key]: true }
  adminActionError.value = ""
  try {
    const reply = await $backend("tournament_registrations", "admin_exportCsv", {
      id: selectedAdminTournament.value.id,
      token: token.value,
      category: key === "all" ? null : key,
    })
    triggerDownload(reply.data, `registrations_${selectedAdminTournament.value.id}${exportFileTag(key)}.csv`)
  } catch (error) {
    adminActionError.value = t("trnreg.admin_export_failed")
  } finally {
    exportingCsv.value = { ...exportingCsv.value, [key]: false }
  }
}

async function exportSwar(key) {
  if (!selectedAdminTournament.value) return
  exportingSwar.value = { ...exportingSwar.value, [key]: true }
  adminActionError.value = ""
  try {
    const reply = await $backend("tournament_registrations", "admin_exportSwar", {
      id: selectedAdminTournament.value.id,
      category: key,
      token: token.value,
    })
    triggerDownload(reply.data, `swar_${selectedAdminTournament.value.id}${exportFileTag(key)}.csv`)
  } catch (error) {
    adminActionError.value = t("trnreg.admin_export_failed")
  } finally {
    exportingSwar.value = { ...exportingSwar.value, [key]: false }
  }
}

async function refreshElo() {
  if (!selectedAdminTournament.value) return
  refreshEloLoading.value = true
  refreshEloResult.value = null
  adminActionError.value = ""
  try {
    const reply = await $backend("tournament_registrations", "admin_refreshElo", {
      id: selectedAdminTournament.value.id,
      token: token.value,
    })
    refreshEloResult.value = reply.data.updated
    await loadAdminRegistrations()
  } catch (error) {
    adminActionError.value = t("trnreg.admin_refresh_elo_failed")
  } finally {
    refreshEloLoading.value = false
  }
}

// ---------------------------------------------------------------------
// mount
// ---------------------------------------------------------------------

onMounted(() => {
  const l = route.query.locale || route.query.lang
  locale.value = ["en", "nl", "fr", "de"].includes(l) ? l : "nl"

  tokenStore.startup()
  if (typeof window !== "undefined") {
    adminName.value = window.localStorage.getItem("tournamentregname") || ""
  }

  // trnId takes priority over an existing admin session: a link to a specific
  // tournament (e.g. "View public page", opened in a new tab) must always land
  // on that tournament's public form, even if this browser also has an admin
  // token cached from another tab. The admin dashboard is still one click away
  // via the nav bar's "Admin" button whenever token is set.
  if (trnId.value) {
    // The list unless the address asks for the form. "form" is still read
    // as the form, and "list" (the confirmation mail's link) as the list.
    view.value = ["register", "form"].includes(route.query.view) ? "form" : "list"
    if (view.value === "list") loadRegistrations()
  } else if (token.value) {
    view.value = "admin"
    loadAdminTournaments()
  } else {
    view.value = "login"
  }

  if (trnId.value) loadTournament()

  // Send message to parent iframe if embedded, matching the other tools/*
  // pages (fide_registration.vue, national_elo_archive.vue, ...)
  if (typeof window !== "undefined" && window.parent !== window) {
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        window.parent.postMessage({
          type: "kbsb-iframe-resize",
          height: entry.target.scrollHeight,
        }, "*")
      }
    })
    resizeObserver.observe(document.body)
  }
})
</script>

<template>
  <v-container class="my-4 trnreg-shell">
    <v-row class="mb-2 align-center" justify="space-between">
      <v-col cols="auto">
        <h1 class="text-h5 font-weight-bold text-green-darken-3">{{ t('trnreg.title') }}</h1>
      </v-col>
      <v-col cols="auto" class="d-flex ga-1">
        <v-btn size="small" variant="text" :active="locale === 'fr'" @click="setLocale('fr')">FR</v-btn>
        <v-btn size="small" variant="text" :active="locale === 'nl'" @click="setLocale('nl')">NL</v-btn>
        <v-btn size="small" variant="text" :active="locale === 'en'" @click="setLocale('en')">EN</v-btn>
        <v-btn size="small" variant="text" :active="locale === 'de'" @click="setLocale('de')">DE</v-btn>
      </v-col>
    </v-row>

    <v-row class="mb-3 align-center" dense>
      <v-col cols="auto" v-if="trnId && view !== 'list'">
        <v-btn size="small" variant="tonal" color="green-darken-2" prepend-icon="mdi-format-list-bulleted" @click="goToList">{{ t('trnreg.nav_list') }}</v-btn>
      </v-col>
      <v-spacer />
      <v-col cols="auto" v-if="!token">
        <v-btn size="small" variant="text" color="grey-darken-1" prepend-icon="mdi-shield-account" @click="goToLogin">{{ t('trnreg.nav_login') }}</v-btn>
      </v-col>
      <template v-else>
        <v-col cols="auto" v-if="view !== 'admin'">
          <v-btn size="small" variant="text" color="green-darken-2" prepend-icon="mdi-view-dashboard" @click="goToAdmin">{{ t('trnreg.nav_admin') }}</v-btn>
        </v-col>
        <v-col cols="auto" class="text-body-2 text-grey-darken-1 d-flex align-center" v-if="adminName">
          {{ t('trnreg.logged_in_as') }}:&nbsp;<strong>{{ adminName }}</strong>
        </v-col>
        <v-col cols="auto">
          <v-btn size="small" variant="text" color="grey-darken-1" prepend-icon="mdi-logout" @click="logout">{{ t('trnreg.nav_logout') }}</v-btn>
        </v-col>
      </template>
    </v-row>

    <v-alert v-if="errorText" type="error" closable class="mb-4" @click:close="errorText = ''">{{ errorText }}</v-alert>

    <!-- ============ tournament header, above both the list and the form ============ -->
    <div v-if="view === 'form' || view === 'list'">
      <div v-if="!trnId" class="text-center py-8 text-grey-darken-1">{{ t('trnreg.no_tournament') }}</div>
      <div v-else>
        <v-row v-if="loadingTournament" justify="center" class="my-8">
          <v-progress-circular indeterminate color="green" />
        </v-row>
        <v-card v-else-if="tournament" class="mb-4 elevation-2 border-green">
          <v-card-text>
            <h2 class="text-h6 font-weight-bold text-green-darken-3 mb-1">{{ tournament.name }}</h2>
            <div class="text-body-2 text-grey-darken-2 mb-2" v-if="tournament.address || tournament.city">
              <strong>{{ t('trnreg.th_location') }}:</strong>
              {{ tournament.address }}<span v-if="tournament.address && tournament.city">, </span>{{ tournament.city }}
            </div>
            <v-row dense class="text-body-2">
              <v-col cols="12" sm="6" md="4">
                <strong>{{ t('trnreg.th_dates') }}:</strong>
                {{ formatDateDisplay(tournament.date_start) }}<span v-if="tournament.date_end && tournament.date_end !== tournament.date_start"> - {{ formatDateDisplay(tournament.date_end) }}</span>
              </v-col>
              <v-col cols="12" sm="6" md="4" v-if="tournament.time_control">
                <strong>{{ t('trnreg.th_time_control') }}:</strong> {{ tempoDisplay(tournament) }}
              </v-col>
              <v-col cols="12" sm="6" md="4" v-if="tournament.closing_registrations">
                <strong>{{ t('trnreg.th_closing') }}:</strong> {{ closingDisplay(tournament.closing_registrations) }}
              </v-col>
              <v-col cols="12" sm="6" md="4" v-if="tournament.obligatory_presence">
                <strong>{{ t('trnreg.th_obligatory_presence') }}:</strong> {{ utcIsoToBrusselsHHMM(tournament.obligatory_presence) }}
              </v-col>
              <v-col cols="12" v-if="tournament.categories && tournament.categories.length">
                <strong>{{ t('trnreg.th_categories') }}:</strong> {{ tournament.categories.join(', ') }}
              </v-col>
              <v-col cols="12" sm="6" v-if="tournament.chief_arbiter_name">
                <strong>{{ t('trnreg.th_arbiter') }}:</strong> {{ tournament.chief_arbiter_name }}
                <span v-if="tournament.chief_arbiter_email">({{ tournament.chief_arbiter_email }})</span>
              </v-col>
              <v-col cols="12" sm="6" v-if="tournament.chief_organizer_name">
                <strong>{{ t('trnreg.th_organizer') }}:</strong> {{ tournament.chief_organizer_name }}
                <span v-if="tournament.chief_organizer_email">({{ tournament.chief_organizer_email }})</span>
              </v-col>
              <v-col cols="12" v-if="tournament.url">
                <strong>{{ t('trnreg.th_website') }}:</strong> <a :href="tournament.url" target="_blank" rel="noopener">{{ tournament.url }}</a>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <div v-if="tournament && view === 'form'">
          <v-alert v-if="registrationsClosed" type="info" variant="tonal" class="elevation-2">
            {{ t('trnreg.registrations_closed') }}
          </v-alert>

          <v-card v-else class="elevation-2">
            <v-card-text>
              <v-alert v-if="regError" type="error" class="mb-4">{{ regError }}</v-alert>
              <v-form ref="regFormRef" @submit.prevent="submitRegistration">
                <div class="trnreg-lookup-wrap mb-3">
                  <v-text-field
                    v-model="lookupQuery"
                    :label="t('trnreg.field_lookup')"
                    variant="outlined"
                    color="green-darken-2"
                    density="compact"
                    autocomplete="off"
                    :hint="t('trnreg.lookup_hint')"
                    persistent-hint
                    @input="onLookupInput"
                    @blur="hideLookupResults"
                  ></v-text-field>
                  <span v-if="lookupSearching" class="trnreg-searching-hint">{{ t('trnreg.lookup_searching') }}</span>
                  <ul v-if="lookupResults.length" class="trnreg-dropdown">
                    <li v-for="p in lookupResults" :key="p.national_id || p.fide_id || p.name" @mousedown.prevent="selectLookupResult(p)">
                      {{ p.name }} <span class="trnreg-dropdown-meta">{{ p.birth_year || '' }} {{ p.club || '' }}</span>
                    </li>
                  </ul>
                  <div v-if="!lookupSearching && lookupQuery.trim().length >= 2 && !lookupResults.length" class="trnreg-searching-hint">{{ t('trnreg.lookup_no_results') }}</div>
                </div>

                <v-row dense>
                  <v-col cols="12" sm="6">
                    <v-text-field v-model="regForm.last_name" :label="t('trnreg.field_last_name')" variant="outlined" color="green-darken-2" density="compact" required class="trnreg-required" :rules="[requiredRule]"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-text-field v-model="regForm.first_name" :label="t('trnreg.field_first_name')" variant="outlined" color="green-darken-2" density="compact" required class="trnreg-required" :rules="[requiredRule]"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-select v-model="regForm.sex" :items="[{ title: t('trnreg.sex_m'), value: 'M' }, { title: t('trnreg.sex_f'), value: 'F' }]" item-title="title" item-value="value" :label="t('trnreg.field_sex')" variant="outlined" color="green-darken-2" density="compact" required class="trnreg-required" :rules="[requiredRule]"></v-select>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.date_birth" type="date" :label="t('trnreg.field_date_birth')" variant="outlined" color="green-darken-2" density="compact" :required="!hasFideId" :class="hasFideId ? '' : 'trnreg-required'" :rules="[birthDateRule]" :hint="hasFideId ? t('trnreg.birth_date_optional_hint') : (matchedBirthYear ? (t('trnreg.birth_year_hint') + ': ' + matchedBirthYear) : '')" persistent-hint></v-text-field>
                  </v-col>
                  <!--
                    Place of birth, country of residence and a free-text
                    nationality box are gone: this page never used the first
                    two for anything, and nationality is the same concept as
                    the FIDE federation box below (see applyLookupResult's
                    own comment), which the lookup already fills in. Asking
                    a third time was noise, not data.
                  -->
                  <v-col cols="12" sm="6">
                    <v-text-field v-model="regForm.phone" :label="t('trnreg.field_phone_gsm')" variant="outlined" color="green-darken-2" density="compact" required class="trnreg-required" :rules="[requiredRule]"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-text-field v-model="regForm.email" type="email" :label="t('trnreg.field_email')" variant="outlined" color="green-darken-2" density="compact" required class="trnreg-required" :rules="[requiredRule]"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.national_id" :label="t('trnreg.field_national_id')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.national_club" :label="t('trnreg.field_national_club')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <!--
                    Affiliation and G-licence are shown, not ticked: they are
                    facts about our records, which the search fills in and
                    the API reads again itself on submit.
                  -->
                  <v-col cols="12" sm="4" class="d-flex align-center ga-2 flex-wrap">
                    <v-chip size="small" variant="tonal" :color="regForm.affiliated === true ? 'green-darken-2' : 'grey'">
                      {{ t('trnreg.field_affiliated') }}: {{ yesNoUnknown(regForm.affiliated) }}
                    </v-chip>
                    <v-chip v-if="regForm.g_license" size="small" variant="tonal" color="blue-darken-2">
                      {{ t('trnreg.field_g_license') }}
                    </v-chip>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.fide_id" :label="t('trnreg.field_fide_id')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" v-if="needsFideIdWarning">
                    <v-alert type="warning" variant="tonal" density="compact">{{ t('trnreg.fide_id_warning') }}</v-alert>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.fide_title" :label="t('trnreg.field_fide_title')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.fide_federation" :label="t('trnreg.field_fide_federation')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <!--
                    Only the rating this tournament is played for. A rapid or
                    blitz tournament shows the standard rating as the
                    fallback when the player has none in its own.
                  -->
                  <v-col cols="12" sm="4">
                    <v-text-field
                      v-model="regForm[ratingField(tournament)]"
                      type="number"
                      :label="t('trnreg.' + ratingField(tournament).replace('fide_rating_', 'field_fide_rating_'))"
                      :hint="ratingField(tournament) !== 'fide_rating_standard' && !(Number(regForm[ratingField(tournament)]) > 0) && Number(regForm.fide_rating_standard) > 0 ? t('trnreg.rating_fallback_hint') + ': ' + regForm.fide_rating_standard : ''"
                      persistent-hint
                      variant="outlined" color="green-darken-2" density="compact"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <!--
                      0 or 1 category: applyCategoryDefault() already picked
                      it, and there is nothing to choose, so the box is
                      locked. 2+: left blank on purpose and required, a
                      default here would silently register somebody in the
                      wrong category.
                    -->
                    <v-select
                      v-model="regForm.category_index"
                      :items="(tournament.categories || []).map((c, i) => ({ title: c, value: i }))"
                      :label="t('trnreg.field_category')"
                      :placeholder="t('trnreg.category_placeholder')"
                      variant="outlined" color="green-darken-2" density="compact"
                      :disabled="(tournament.categories || []).length <= 1"
                      :required="(tournament.categories || []).length > 1"
                      :class="(tournament.categories || []).length > 1 ? 'trnreg-required' : ''"
                      :rules="(tournament.categories || []).length > 1 ? [requiredRule] : []"
                    ></v-select>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-text-field v-model="regForm.rounds_absent" :label="t('trnreg.field_rounds_absent')" variant="outlined" color="green-darken-2" density="compact" :rules="[roundsAbsentRule]"></v-text-field>
                  </v-col>
                  <!--
                    The "contact person" box is gone: the registrant is the
                    contact, by name, phone/GSM and e-mail above, and this
                    duplicated that without ever being required or checked.
                  -->
                  <v-col cols="12">
                    <v-textarea v-model="regForm.note" :label="t('trnreg.field_note')" variant="outlined" color="green-darken-2" density="compact" rows="2"></v-textarea>
                  </v-col>
                </v-row>

                <v-btn type="submit" color="green-darken-2" :loading="regSubmitting" class="mt-2">{{ t('trnreg.submit_btn') }}</v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </div>
      </div>
    </div>

    <!-- ============ VIEW: public listing ============ -->
    <div v-if="view === 'list' && trnId">
      <v-alert v-if="submittedRegistration" type="success" variant="tonal" closable class="mb-4" @click:close="submittedRegistration = null">
        <div class="font-weight-bold">{{ t('trnreg.submitted_title') }}</div>
        <div>{{ t('trnreg.submitted_msg') }}</div>
        <div class="mt-1">{{ t('trnreg.registration_id_label') }}: <strong>{{ submittedRegistration.id }}</strong></div>
      </v-alert>
      <div v-if="tournament && !registrationsClosed" class="mb-3">
        <v-btn color="green-darken-2" prepend-icon="mdi-account-plus" @click="goToForm">
          {{ submittedRegistration ? t('trnreg.register_another') : t('trnreg.nav_form') }}
        </v-btn>
      </div>
      <v-row class="mb-2 align-center" dense>
        <v-col cols="12" sm="6">
          <h2 class="text-h6 font-weight-bold text-green-darken-3">
            {{ t('trnreg.list_title') }}<span v-if="tournament"> - {{ tournament.name }}</span>
            <span class="text-body-2 text-grey-darken-1 font-weight-regular"> ({{ sortedRegistrations.length }} {{ t('trnreg.list_count') }})</span>
          </h2>
        </v-col>
        <v-col cols="12" sm="6">
          <v-text-field v-model="listFilter" :label="t('trnreg.list_filter')" variant="outlined" density="compact" color="green-darken-2" prepend-inner-icon="mdi-magnify" hide-details clearable></v-text-field>
        </v-col>
      </v-row>

      <v-row v-if="loadingRegistrations" justify="center" class="my-8">
        <v-progress-circular indeterminate color="green" />
      </v-row>
      <v-card v-else class="elevation-2">
        <v-card-text class="pa-0">
          <div v-if="!sortedRegistrations.length" class="text-center py-8 text-grey-darken-1">{{ t('trnreg.list_empty') }}</div>
          <div v-else class="trnreg-table-scroll">
            <v-table hover>
              <thead class="bg-green-lighten-5">
                <tr>
                  <th style="cursor:pointer;user-select:none;" @click="toggleListSort('last_name')">{{ t('trnreg.col_name') }} <v-icon size="small">{{ listSortKey === 'last_name' ? (listSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}</v-icon></th>
                  <th style="cursor:pointer;user-select:none;" @click="toggleListSort('sex')">{{ t('trnreg.col_sex') }}</th>
                  <th style="cursor:pointer;user-select:none;" @click="toggleListSort('birth_year')">{{ t('trnreg.col_birth') }} <v-icon size="small">{{ listSortKey === 'birth_year' ? (listSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}</v-icon></th>
                  <th style="cursor:pointer;user-select:none;" @click="toggleListSort('national_club')">{{ t('trnreg.col_club') }}</th>
                  <th>{{ t('trnreg.col_category') }}</th>
                  <th style="cursor:pointer;user-select:none;" @click="toggleListSort('fide_id')">{{ t('trnreg.col_fide_id') }}</th>
                  <th style="cursor:pointer;user-select:none;" @click="toggleListSort('rating')">{{ t('trnreg.col_rating') }} <v-icon size="small">{{ listSortKey === 'rating' ? (listSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}</v-icon></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in sortedRegistrations" :key="r.id">
                  <td>{{ r.last_name }} {{ r.first_name }}</td>
                  <td>{{ r.sex }}</td>
                  <!-- Birth YEAR only, never the full date -- this is the
                       public listing (no auth beyond x-api-key). See
                       PUBLIC_REGISTRATION_COLUMNS server-side; matches
                       legacy's own listingRegistrations.js, which fetched
                       full data but deliberately truncated it to
                       DateBirth.substring(0, 4) before ever rendering it. -->
                  <td>{{ r.birth_year || "" }}</td>
                  <td>{{ r.national_club_name || r.national_club }}</td>
                  <td>{{ categoryLabel(tournament, r.category_index) }}</td>
                  <td>{{ r.fide_id }}</td>
                  <td>{{ effectiveRating(r, tournament) || '' }}</td>
                </tr>
              </tbody>
            </v-table>
          </div>
        </v-card-text>
      </v-card>
    </div>

    <!-- ============ VIEW: admin login ============ -->
    <div v-if="view === 'login'" class="d-flex justify-center">
      <v-card class="elevation-2" style="max-width: 420px; width: 100%;">
        <v-card-text>
          <h2 class="text-h6 font-weight-bold text-green-darken-3 mb-3">{{ t('trnreg.login_title') }}</h2>
          <v-alert v-if="loginError" type="error" class="mb-3">{{ loginError }}</v-alert>

          <p class="text-body-2 mb-3">{{ t('trnreg.odoo_login_intro') }}</p>
          <!--
            Plain name/id on both boxes, so a password manager recognises them
            as one login: without them Bitwarden filled the e-mail and left the
            password empty.
          -->
          <v-form id="odoo-login-form" name="odoo-login" @submit.prevent="submitOdooLogin">
            <v-text-field v-model="odooEmail" id="odoo-login-email" name="username" type="email" :label="t('trnreg.field_odoo_email')" variant="outlined" color="green-darken-2" density="comfortable" autocomplete="username" required></v-text-field>
            <v-text-field v-model="odooPassword" id="odoo-login-password" name="password" type="password" :label="t('trnreg.field_password')" variant="outlined" color="green-darken-2" density="comfortable" autocomplete="current-password" required></v-text-field>
            <v-btn type="submit" color="green-darken-2" block :loading="loginSubmitting">{{ t('trnreg.odoo_login_btn') }}</v-btn>
          </v-form>
          <div class="text-caption text-medium-emphasis mt-2">{{ t('trnreg.odoo_login_2fa_note') }}</div>

          <v-divider class="my-4" />
          <v-btn variant="text" size="small" color="grey-darken-1" :prepend-icon="showPasswordLogin ? 'mdi-chevron-down' : 'mdi-chevron-right'" @click="showPasswordLogin = !showPasswordLogin">
            {{ t('trnreg.password_login_toggle') }}
          </v-btn>
          <v-form v-if="showPasswordLogin" id="arbiter-login-form" name="arbiter-login" class="mt-3" @submit.prevent="submitLogin">
            <v-text-field v-model="loginUsername" id="arbiter-login-username" name="arbiter-username" :label="t('trnreg.field_username')" variant="outlined" color="green-darken-2" density="comfortable" autocomplete="username" required></v-text-field>
            <v-text-field v-model="loginPassword" id="arbiter-login-password" name="arbiter-password" type="password" :label="t('trnreg.field_password')" variant="outlined" color="green-darken-2" density="comfortable" autocomplete="current-password" required></v-text-field>
            <v-btn type="submit" color="green-darken-2" variant="tonal" block :loading="loginSubmitting">{{ t('trnreg.login_btn') }}</v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </div>

    <!-- ============ VIEW: admin dashboard ============ -->
    <div v-if="view === 'admin' && token">
      <v-alert v-if="adminActionError" type="error" closable class="mb-4" @click:close="adminActionError = ''">{{ adminActionError }}</v-alert>
      <v-alert v-if="adminActionNotice" type="success" closable class="mb-4" @click:close="adminActionNotice = ''">{{ adminActionNotice }}</v-alert>

      <div v-if="!selectedAdminTournament">
        <v-row class="mb-2 align-center" justify="space-between">
          <v-col cols="auto"><h2 class="text-h6 font-weight-bold text-green-darken-3">{{ t('trnreg.admin_title') }}</h2></v-col>
          <v-col cols="auto"><v-btn color="green-darken-2" prepend-icon="mdi-plus" @click="openNewTournament">{{ t('trnreg.admin_new_tournament') }}</v-btn></v-col>
        </v-row>

        <v-row v-if="loadingAdminTournaments" justify="center" class="my-8">
          <v-progress-circular indeterminate color="green" />
        </v-row>
        <div v-else-if="!adminTournaments.length" class="text-center py-8 text-grey-darken-1">{{ t('trnreg.admin_no_tournaments') }}</div>
        <template v-else>
          <div v-if="!activeAdminTournaments.length" class="text-center py-6 text-grey-darken-1">{{ t('trnreg.admin_no_active_tournaments') }}</div>
          <v-row dense>
            <v-col cols="12" md="6" lg="4" v-for="trn in activeAdminTournaments" :key="trn.id">
              <v-card class="elevation-2 h-100">
                <v-card-text>
                  <h3 class="text-subtitle-1 font-weight-bold text-green-darken-3">{{ trn.name }}</h3>
                  <div class="text-body-2 text-grey-darken-2">
                    {{ formatDateDisplay(trn.date_start) }}<span v-if="trn.date_end && trn.date_end !== trn.date_start"> - {{ formatDateDisplay(trn.date_end) }}</span>
                  </div>
                  <div class="text-body-2 text-grey-darken-2" v-if="trn.city">{{ trn.city }}</div>
                  <v-chip v-if="!isMine(trn)" size="x-small" variant="tonal" color="blue-darken-2" class="mt-1">{{ t('trnreg.share_shared_chip') }}</v-chip>
                  <div class="d-flex flex-wrap ga-2 mt-3">
                    <v-btn size="small" color="green-darken-2" variant="tonal" @click="selectAdminTournament(trn)">{{ t('trnreg.admin_manage_registrations') }}</v-btn>
                    <v-btn size="small" variant="text" color="grey-darken-1" @click="openEditTournament(trn)">{{ t('trnreg.admin_edit_tournament') }}</v-btn>
                    <v-btn size="small" variant="text" color="grey-darken-1" prepend-icon="mdi-content-copy" @click="openCopyTournament(trn)">{{ t('trnreg.admin_copy_tournament') }}</v-btn>
                    <v-btn size="small" variant="text" color="green-darken-2" prepend-icon="mdi-open-in-new" :href="publicTournamentUrl(trn)" target="_blank" rel="noopener">{{ t('trnreg.admin_view_public_page') }}</v-btn>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <div v-if="archivedAdminTournaments.length" class="mt-6">
            <v-btn variant="text" color="grey-darken-1" :prepend-icon="showArchived ? 'mdi-chevron-down' : 'mdi-chevron-right'" @click="showArchived = !showArchived">
              {{ t('trnreg.admin_archived') }} ({{ archivedAdminTournaments.length }})
            </v-btn>
            <v-row v-if="showArchived" dense class="mt-1">
              <v-col cols="12" md="6" lg="4" v-for="trn in archivedAdminTournaments" :key="'arch-' + trn.id">
                <v-card class="elevation-1 h-100" color="grey-lighten-4">
                  <v-card-text>
                    <h3 class="text-subtitle-1 font-weight-bold text-grey-darken-2">{{ trn.name }}</h3>
                    <div class="text-body-2 text-grey-darken-2">
                      {{ formatDateDisplay(trn.date_start) }}<span v-if="trn.date_end && trn.date_end !== trn.date_start"> - {{ formatDateDisplay(trn.date_end) }}</span>
                    </div>
                    <div class="d-flex flex-wrap ga-2 mt-3">
                      <v-btn size="small" variant="tonal" color="grey-darken-2" @click="selectAdminTournament(trn)">{{ t('trnreg.admin_manage_registrations') }}</v-btn>
                      <v-btn size="small" variant="text" color="grey-darken-1" prepend-icon="mdi-content-copy" @click="openCopyTournament(trn)">{{ t('trnreg.admin_copy_tournament') }}</v-btn>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </div>
        </template>
      </div>

      <div v-else>
        <v-btn size="small" variant="text" color="green-darken-2" prepend-icon="mdi-arrow-left" class="mb-3" @click="backToTournamentList">{{ t('trnreg.admin_back_to_tournaments') }}</v-btn>

        <v-card class="mb-4 elevation-2">
          <v-card-text>
            <v-row align="center" justify="space-between">
              <v-col cols="12" md="auto">
                <h2 class="text-h6 font-weight-bold text-green-darken-3">{{ selectedAdminTournament.name }}</h2>
                <div class="text-body-2 text-grey-darken-2">
                  {{ formatDateDisplay(selectedAdminTournament.date_start) }}<span v-if="selectedAdminTournament.date_end && selectedAdminTournament.date_end !== selectedAdminTournament.date_start"> - {{ formatDateDisplay(selectedAdminTournament.date_end) }}</span>
                </div>
              </v-col>
              <v-col cols="12" md="auto" class="d-flex flex-wrap ga-2">
                <v-btn size="small" variant="text" color="grey-darken-1" prepend-icon="mdi-pencil" @click="openEditTournament(selectedAdminTournament)">{{ t('trnreg.admin_edit_tournament') }}</v-btn>
                <v-btn size="small" variant="text" color="grey-darken-1" prepend-icon="mdi-content-copy" @click="openCopyTournament(selectedAdminTournament)">{{ t('trnreg.admin_copy_tournament') }}</v-btn>
                <v-btn size="small" variant="text" color="green-darken-2" prepend-icon="mdi-open-in-new" :href="publicTournamentUrl(selectedAdminTournament)" target="_blank" rel="noopener">{{ t('trnreg.admin_view_public_page') }}</v-btn>
                <v-btn v-if="isMine(selectedAdminTournament)" size="small" variant="text" color="red-darken-2" prepend-icon="mdi-delete" @click="openDeleteTournament(selectedAdminTournament)">{{ t('trnreg.admin_delete_tournament') }}</v-btn>
                <template v-for="x in exportTargets" :key="'exp-' + x.key">
                  <v-btn size="small" variant="tonal" color="green-darken-2" prepend-icon="mdi-download" :loading="!!exportingCsv[x.key]" @click="exportCsv(x.key)">{{ t('trnreg.admin_export_csv') }}<span v-if="x.label">&nbsp;({{ x.label }})</span></v-btn>
                  <v-btn size="small" variant="tonal" color="green-darken-2" prepend-icon="mdi-download" :loading="!!exportingSwar[x.key]" @click="exportSwar(x.key)">{{ t('trnreg.admin_export_swar') }}<span v-if="x.label">&nbsp;({{ x.label }})</span></v-btn>
                </template>
                <v-btn size="small" variant="tonal" color="blue-darken-2" prepend-icon="mdi-refresh" :loading="refreshEloLoading" @click="refreshElo">{{ t('trnreg.admin_refresh_elo') }}</v-btn>
              </v-col>
            </v-row>
            <v-alert v-if="refreshEloResult !== null" type="success" density="compact" class="mt-3">
              {{ t('trnreg.admin_refresh_elo_result').replace('{count}', refreshEloResult) }}
            </v-alert>
          </v-card-text>
        </v-card>

        <!--
          Sharing: other admins by member number. They manage the tournament
          like the owner, except deleting it and changing this list, which
          only the owner can do.
        -->
        <v-card class="mb-4 elevation-1">
          <v-card-text>
            <div class="text-subtitle-2 font-weight-bold text-green-darken-3 mb-1">{{ t('trnreg.share_title') }}</div>
            <div v-if="!isMine(selectedAdminTournament)" class="text-body-2 text-grey-darken-1 mb-2">{{ t('trnreg.share_shared_with_you') }}</div>
            <v-alert v-if="adminsError" type="error" density="compact" class="mb-2">{{ adminsError }}</v-alert>
            <div v-if="!tournamentAdmins.length" class="text-body-2 text-grey-darken-1">{{ t('trnreg.share_none') }}</div>
            <div v-for="a in tournamentAdmins" :key="a.national_id" class="d-flex align-center ga-2">
              <span class="text-body-2">{{ a.name || '?' }} <span class="text-grey-darken-1">#{{ a.national_id }}</span></span>
              <v-btn v-if="isMine(selectedAdminTournament)" size="x-small" variant="text" color="red-darken-2" :disabled="adminsBusy" @click="removeTournamentAdmin(a)">{{ t('trnreg.share_remove') }}</v-btn>
            </div>
            <v-form v-if="isMine(selectedAdminTournament)" class="d-flex align-start ga-2 mt-2" @submit.prevent="addTournamentAdmin">
              <v-text-field
                v-model="newAdminNationalId"
                :label="t('trnreg.share_member_number')"
                variant="outlined" color="green-darken-2" density="compact" hide-details
                style="max-width: 220px"
              ></v-text-field>
              <v-btn type="submit" color="green-darken-2" variant="tonal" :loading="adminsBusy">{{ t('trnreg.share_add') }}</v-btn>
            </v-form>
          </v-card-text>
        </v-card>

        <h3 class="text-subtitle-1 font-weight-bold text-green-darken-3 mb-2">
          {{ t('trnreg.list_title') }}
          <span class="text-body-2 text-grey-darken-1 font-weight-regular"> ({{ adminRegistrations.length }} {{ t('trnreg.list_count') }})</span>
        </h3>

        <v-row v-if="loadingAdminRegistrations" justify="center" class="my-8">
          <v-progress-circular indeterminate color="green" />
        </v-row>
        <v-card v-else class="elevation-2">
          <v-card-text class="pa-0">
            <div v-if="!adminRegistrations.length" class="text-center py-8 text-grey-darken-1">{{ t('trnreg.list_empty') }}</div>
            <div v-else class="trnreg-table-scroll">
              <v-table hover>
                <thead class="bg-green-lighten-5">
                  <tr>
                    <th style="cursor:pointer;user-select:none;" @click="toggleAdminListSort('id')">{{ t('trnreg.col_id') }} <v-icon size="small">{{ adminListSortKey === 'id' ? (adminListSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}</v-icon></th>
                    <th style="cursor:pointer;user-select:none;" @click="toggleAdminListSort('last_name')">{{ t('trnreg.col_name') }} <v-icon size="small">{{ adminListSortKey === 'last_name' ? (adminListSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}</v-icon></th>
                    <th>{{ t('trnreg.col_sex') }}</th>
                    <th style="cursor:pointer;user-select:none;" @click="toggleAdminListSort('date_birth')">{{ t('trnreg.col_birth') }} <v-icon size="small">{{ adminListSortKey === 'date_birth' ? (adminListSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}</v-icon></th>
                    <th>{{ t('trnreg.col_club') }}</th>
                    <th>{{ t('trnreg.col_category') }}</th>
                    <th>{{ t('trnreg.col_fide_id') }}</th>
                    <th style="cursor:pointer;user-select:none;" @click="toggleAdminListSort('rating')">{{ t('trnreg.col_rating') }} <v-icon size="small">{{ adminListSortKey === 'rating' ? (adminListSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}</v-icon></th>
                    <th>{{ t('trnreg.col_email') }}</th>
                    <th>{{ t('trnreg.col_phone') }}</th>
                    <th>{{ t('trnreg.col_actions') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="r in sortedAdminRegistrations" :key="r.id">
                    <td>{{ r.id }}</td>
                    <td>{{ r.last_name }} {{ r.first_name }}</td>
                    <td>{{ r.sex }}</td>
                    <td>{{ formatDateDisplay(r.date_birth) }}</td>
                    <td>{{ r.national_club_name || r.national_club }}</td>
                    <td>{{ categoryLabel(selectedAdminTournament, r.category_index) }}</td>
                    <td>{{ r.fide_id }}</td>
                    <td>{{ effectiveRating(r, selectedAdminTournament) || '' }}</td>
                    <td>{{ r.email }}</td>
                    <td>{{ r.phone || r.gsm }}</td>
                    <td class="text-no-wrap">
                      <v-btn size="small" variant="text" color="green-darken-2" @click="openEditRegistration(r)">{{ t('trnreg.edit_btn') }}</v-btn>
                      <v-btn size="small" variant="text" color="red-darken-2" @click="deleteRegistration(r)">{{ t('trnreg.delete_btn') }}</v-btn>
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </div>
          </v-card-text>
        </v-card>
      </div>
    </div>

    <!-- ============ dialog: edit registration (public self-edit / admin) ============ -->
    <v-dialog v-model="editRegDialog" max-width="900" scrollable>
      <v-card>
        <v-card-title>{{ t('trnreg.edit_registration_title') }}</v-card-title>
        <v-card-text>
          <v-alert v-if="editRegError" type="error" class="mb-3">{{ editRegError }}</v-alert>

          <div class="trnreg-lookup-wrap mb-3">
            <v-text-field
              v-model="editRegLookupQuery"
              :label="t('trnreg.field_lookup')"
              variant="outlined" color="green-darken-2" density="compact" autocomplete="off"
              :hint="t('trnreg.lookup_hint')" persistent-hint
              @input="onEditRegLookupInput"
              @blur="editRegLookupResults = []"
            ></v-text-field>
            <span v-if="editRegLookupSearching" class="trnreg-searching-hint">{{ t('trnreg.lookup_searching') }}</span>
            <ul v-if="editRegLookupResults.length" class="trnreg-dropdown">
              <li v-for="p in editRegLookupResults" :key="p.national_id || p.fide_id || p.name" @mousedown.prevent="selectEditRegLookupResult(p)">
                {{ p.name }} <span class="trnreg-dropdown-meta">{{ p.birth_year || '' }} {{ p.club || '' }}</span>
              </li>
            </ul>
          </div>

          <v-row dense>
            <v-col cols="12" sm="6"><v-text-field v-model="editRegForm.last_name" :label="t('trnreg.field_last_name')" variant="outlined" color="green-darken-2" density="compact" required class="trnreg-required"></v-text-field></v-col>
            <v-col cols="12" sm="6"><v-text-field v-model="editRegForm.first_name" :label="t('trnreg.field_first_name')" variant="outlined" color="green-darken-2" density="compact" required class="trnreg-required"></v-text-field></v-col>
            <v-col cols="12" sm="4">
              <v-select v-model="editRegForm.sex" :items="[{ title: t('trnreg.sex_m'), value: 'M' }, { title: t('trnreg.sex_f'), value: 'F' }]" item-title="title" item-value="value" :label="t('trnreg.field_sex')" variant="outlined" color="green-darken-2" density="compact"></v-select>
            </v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="editRegForm.date_birth" type="date" :label="t('trnreg.field_date_birth')" variant="outlined" color="green-darken-2" density="compact" required class="trnreg-required"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="editRegForm.place_birth" :label="t('trnreg.field_place_birth')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="6"><v-text-field v-model="editRegForm.country_residence" :label="t('trnreg.field_country_residence')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="6"><v-text-field v-model="editRegForm.nationality" :label="t('trnreg.field_nationality')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="editRegForm.phone" :label="t('trnreg.field_phone')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="editRegForm.gsm" :label="t('trnreg.field_gsm')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="editRegForm.email" type="email" :label="t('trnreg.field_email')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="editRegForm.national_id" :label="t('trnreg.field_national_id')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="editRegForm.national_club" :label="t('trnreg.field_national_club')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4" class="d-flex align-center"><v-checkbox v-model="editRegForm.affiliated" :label="t('trnreg.field_affiliated')" color="green-darken-2" density="compact" hide-details></v-checkbox></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="editRegForm.fide_id" :label="t('trnreg.field_fide_id')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="editRegForm.fide_title" :label="t('trnreg.field_fide_title')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="editRegForm.fide_federation" :label="t('trnreg.field_fide_federation')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="editRegForm.fide_rating_standard" type="number" :label="t('trnreg.field_fide_rating_standard')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="editRegForm.fide_rating_rapid" type="number" :label="t('trnreg.field_fide_rating_rapid')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="editRegForm.fide_rating_blitz" type="number" :label="t('trnreg.field_fide_rating_blitz')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="6">
              <v-select
                v-model="editRegForm.category_index"
                :items="editRegCategories.map((c, i) => ({ title: c, value: i }))"
                :label="t('trnreg.field_category')" :placeholder="t('trnreg.category_placeholder')"
                variant="outlined" color="green-darken-2" density="compact"
              ></v-select>
            </v-col>
            <v-col cols="12" sm="6"><v-text-field v-model="editRegForm.rounds_absent" :label="t('trnreg.field_rounds_absent')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="6" class="d-flex align-center"><v-checkbox v-model="editRegForm.g_license" :label="t('trnreg.field_g_license')" color="green-darken-2" density="compact" hide-details></v-checkbox></v-col>
            <v-col cols="12"><v-textarea v-model="editRegForm.note" :label="t('trnreg.field_note')" variant="outlined" color="green-darken-2" density="compact" rows="2"></v-textarea></v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeEditRegistration">{{ t('trnreg.cancel_btn') }}</v-btn>
          <v-btn color="green-darken-2" :loading="editRegSubmitting" @click="saveEditRegistration">{{ t('trnreg.update_btn') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ============ dialog: create/edit tournament (admin) ============ -->
    <v-dialog v-model="tournamentFormDialog" max-width="900" scrollable>
      <v-card>
        <v-card-title>{{ tournamentFormMode === 'create' ? t('trnreg.admin_new_tournament') : t('trnreg.admin_edit_tournament') }}</v-card-title>
        <v-card-text>
          <v-alert v-if="tournamentFormError" type="error" class="mb-3">{{ tournamentFormError }}</v-alert>
          <v-row dense>
            <v-col cols="12" sm="8"><v-text-field v-model="tournamentForm.name" :label="t('trnreg.field_name')" variant="outlined" color="green-darken-2" density="compact" required class="trnreg-required"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.city" :label="t('trnreg.field_city')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12"><v-text-field v-model="tournamentForm.address" :label="t('trnreg.field_address')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>

            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.date_start" type="date" :label="t('trnreg.field_date_start')" variant="outlined" color="green-darken-2" density="compact" required class="trnreg-required"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.date_end" type="date" :min="tournamentForm.date_start || undefined" :label="t('trnreg.field_date_end')" variant="outlined" color="green-darken-2" density="compact" @focus="prefillFrom('date_end', 'date_start')"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="obligatoryPresenceTime" type="time" :label="t('trnreg.field_obligatory_presence')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>

            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.opening_registrations" type="date" :label="t('trnreg.field_opening_registrations')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.closing_registrations" type="date" :min="tournamentForm.opening_registrations || undefined" :max="tournamentForm.date_start || undefined" :label="t('trnreg.field_closing_registrations')" variant="outlined" color="green-darken-2" density="compact" @focus="prefillFrom('closing_registrations', 'opening_registrations')"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="closingTime" type="time" :label="t('trnreg.field_closing_time')" :hint="t('trnreg.closing_time_hint')" persistent-hint variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>

            <v-col cols="12" sm="4">
              <v-select v-model="tournamentForm.system" :items="SYSTEM_OPTIONS.map((s) => ({ title: t('trnreg.system_' + s), value: s }))" :label="t('trnreg.field_system')" variant="outlined" color="green-darken-2" density="compact"
                :hint="tournamentForm.system === 'SWISS_BAKU' ? t('trnreg.system_baku_hint') : ''" persistent-hint></v-select>
            </v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.rounds" type="number" :label="t('trnreg.field_rounds')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4">
              <v-select v-model="tournamentForm.time_control" :items="TIME_CONTROL_OPTIONS.map((s) => ({ title: t('trnreg.tc_' + s), value: s }))" :label="t('trnreg.field_time_control')" variant="outlined" color="green-darken-2" density="compact"></v-select>
            </v-col>
            <!-- Directly under the tempo it depends on. -->
            <v-col cols="12" sm="8">
              <v-select
                v-model="tournamentForm.swar_cadence_number"
                :items="cadenceOptions"
                :label="t('trnreg.field_swar_cadence_number')"
                :disabled="!tournamentForm.time_control"
                :hint="tournamentForm.time_control ? '' : t('trnreg.cadence_needs_time_control')"
                :persistent-hint="!tournamentForm.time_control"
                clearable
                variant="outlined" color="green-darken-2" density="compact"
              ></v-select>
            </v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.time_control_details" :label="t('trnreg.field_time_control_details')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>

            <v-col cols="12">
              <div class="text-body-2 font-weight-bold mb-1">{{ t('trnreg.field_categories') }}</div>
              <div v-for="(c, i) in tournamentForm.categories" :key="i" class="d-flex align-center ga-2 mb-2">
                <v-text-field v-model="tournamentForm.categories[i]" :maxlength="SWAR_MAX_CATEGORY_LENGTH" density="compact" variant="outlined" color="green-darken-2" hide-details></v-text-field>
                <v-btn icon size="small" variant="text" color="red-darken-2" @click="removeCategoryRow(i)"><v-icon>mdi-close</v-icon></v-btn>
              </div>
              <v-btn size="small" variant="text" color="green-darken-2" prepend-icon="mdi-plus" :disabled="tournamentForm.categories.length >= SWAR_MAX_CATEGORIES" @click="addCategoryRow">{{ t('trnreg.add_category') }}</v-btn>
              <v-checkbox
                v-model="tournamentForm.export_per_category"
                :label="t('trnreg.field_export_per_category')"
                :hint="t('trnreg.export_per_category_hint')"
                persistent-hint
                color="green-darken-2" density="compact"
              ></v-checkbox>
            </v-col>

            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.url" :label="t('trnreg.field_url')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.organizing_club" :label="t('trnreg.field_organizing_club')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4">
              <v-combobox
                v-model="tournamentForm.federation"
                :items="FEDERATION_OPTIONS"
                :label="t('trnreg.field_federation')"
                :hint="t('trnreg.federation_hint')"
                persistent-hint
                maxlength="10"
                variant="outlined" color="green-darken-2" density="compact"
              ></v-combobox>
            </v-col>

            <v-col cols="12">
              <v-checkbox
                v-model="tournamentForm.fide_homologated"
                :label="t('trnreg.field_fide_homologated')"
                :hint="t('trnreg.fide_homologated_hint')"
                persistent-hint
                color="green-darken-2" density="compact"
              ></v-checkbox>
            </v-col>
            <!--
              SWAR takes one FIDE event code per file (line 12): one for the
              tournament, or one per category when it is exported per
              category, since each category is then its own event.
            -->
            <template v-if="tournamentForm.fide_homologated">
              <v-col v-for="(label, i) in eventCodeSlots" :key="'code-' + i" cols="12" sm="4">
                <v-text-field
                  v-model="tournamentForm.event_codes[i]"
                  :label="label ? t('trnreg.field_event_code_for').replace('{category}', label) : t('trnreg.field_event_code')"
                  inputmode="numeric"
                  variant="outlined" color="green-darken-2" density="compact"
                ></v-text-field>
              </v-col>
              <v-col cols="12" class="text-caption text-medium-emphasis mt-n2">{{ eventCodeSlots.length > 1 ? t('trnreg.event_code_per_category_hint') : t('trnreg.rule_event_code_required') }}</v-col>
            </template>

            <!-- ============ SWAR: tie-breaks and round dates ============ -->
            <v-col cols="12"><div class="text-subtitle-2 font-weight-bold text-green-darken-3 mt-2">{{ t('trnreg.section_swar') }}</div></v-col>
            <v-col cols="12" sm="6">
              <v-select
                v-model="tournamentForm.tiebreak_system"
                :items="TIEBREAK_SYSTEMS.map((s) => ({ title: t('trnreg.tbsys' + s), value: s }))"
                :label="t('trnreg.field_tiebreak_system')"
                clearable
                variant="outlined" color="green-darken-2" density="compact"
              ></v-select>
            </v-col>
            <v-col cols="12" sm="6" class="text-caption text-medium-emphasis">
              {{ tournamentForm.tiebreak_system ? t('trnreg.tbsys_hint' + tournamentForm.tiebreak_system) : t('trnreg.tbsys_none_hint') }}
            </v-col>
            <v-col v-if="tournamentForm.tiebreak_system === '_TB_PERSONEL'" cols="12">
              <div v-for="(n, i) in tournamentForm.tiebreaks" :key="'tb-' + i" class="d-flex align-center ga-2 mb-2">
                <span class="text-body-2" style="min-width: 1.5em">{{ i + 1 }}.</span>
                <v-select
                  v-model="tournamentForm.tiebreaks[i]"
                  :items="TIEBREAK_CODES.map((c) => ({ title: t('trnreg.tb_' + String(c).padStart(2, '0')), value: c }))"
                  variant="outlined" color="green-darken-2" density="compact" hide-details
                ></v-select>
                <v-btn icon size="small" variant="text" color="red-darken-2" @click="removeTiebreakRow(i)"><v-icon>mdi-close</v-icon></v-btn>
              </div>
              <v-btn size="small" variant="text" color="green-darken-2" prepend-icon="mdi-plus" :disabled="tournamentForm.tiebreaks.length >= MAX_TIEBREAKS" @click="addTiebreakRow">{{ t('trnreg.add_tiebreak') }}</v-btn>
              <div class="text-caption text-medium-emphasis">{{ t('trnreg.tiebreak_max_hint') }}</div>
            </v-col>

            <v-col cols="12">
              <div class="text-body-2 font-weight-bold mb-1">{{ t('trnreg.field_round_dates') }}</div>
              <div v-if="!roundDateSlots.length" class="text-caption text-medium-emphasis">{{ t('trnreg.round_dates_need_rounds') }}</div>
              <template v-else>
                <v-row dense>
                  <v-col v-for="r in roundDateSlots" :key="'rd-' + r" cols="6" sm="3" md="2">
                    <v-text-field
                      v-model="tournamentForm.round_dates[r - 1]"
                      type="date"
                      :min="tournamentForm.date_start || undefined"
                      :max="tournamentForm.date_end || undefined"
                      :label="t('trnreg.round_n').replace('{n}', r)"
                      variant="outlined" color="green-darken-2" density="compact" hide-details
                    ></v-text-field>
                  </v-col>
                </v-row>
                <div class="d-flex align-center ga-2 mt-1">
                  <v-btn size="small" variant="text" color="green-darken-2" prepend-icon="mdi-calendar-arrow-right" :disabled="!tournamentForm.round_dates[0] && !tournamentForm.date_start" @click="fillRoundDatesDaily">{{ t('trnreg.round_dates_fill_daily') }}</v-btn>
                  <span class="text-caption text-medium-emphasis">{{ t('trnreg.round_dates_hint') }}</span>
                </div>
              </template>
            </v-col>

            <v-col cols="12"><div class="text-subtitle-2 font-weight-bold text-green-darken-3 mt-2">{{ t('trnreg.section_arbiters') }}</div></v-col>
            <v-col cols="12" sm="8">
              <div class="trnreg-lookup-wrap">
                <v-text-field
                  v-model="arbiterLookup.chief_arbiter.query"
                  :label="t('trnreg.field_chief_arbiter_search')"
                  variant="outlined" color="green-darken-2" density="compact" autocomplete="off"
                  :hint="t('trnreg.lookup_hint')" persistent-hint
                  @input="onArbiterLookupInput('chief_arbiter')"
                  @blur="hideArbiterLookupResults('chief_arbiter')"
                ></v-text-field>
                <span v-if="arbiterLookup.chief_arbiter.searching" class="trnreg-searching-hint">{{ t('trnreg.lookup_searching') }}</span>
                <ul v-if="arbiterLookup.chief_arbiter.results.length" class="trnreg-dropdown">
                  <li v-for="p in arbiterLookup.chief_arbiter.results" :key="p.fide_id || p.national_id || p.name" @mousedown.prevent="selectArbiterLookupResult('chief_arbiter', p)">
                    {{ p.name }} <span class="trnreg-dropdown-meta">{{ p.fide_id || '' }} {{ p.club || '' }}</span>
                  </li>
                </ul>
                <div v-if="!arbiterLookup.chief_arbiter.searching && arbiterLookup.chief_arbiter.query.trim().length >= 2 && !arbiterLookup.chief_arbiter.results.length" class="trnreg-searching-hint">{{ t('trnreg.lookup_no_results') }}</div>
              </div>
              <div class="text-body-2 mt-1">
                <template v-if="tournamentForm.chief_arbiter_name || tournamentForm.chief_arbiter_person_id">
                  {{ t('trnreg.selected_person') }}: <strong>{{ tournamentForm.chief_arbiter_name }}</strong>
                  <span class="text-grey-darken-1">({{ t('trnreg.field_fide_id') }}: {{ tournamentForm.chief_arbiter_person_id || t('trnreg.no_fide_id') }})</span>
                  <v-btn size="x-small" variant="text" color="red-darken-2" @click="clearArbiterSelection('chief_arbiter')">{{ t('trnreg.clear_selection') }}</v-btn>
                </template>
                <span v-else class="text-grey-darken-1">{{ t('trnreg.no_person_selected') }}</span>
              </div>
            </v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.chief_arbiter_email" :label="t('trnreg.field_chief_arbiter_email')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.chief_arbiter_phone" :label="t('trnreg.field_chief_arbiter_phone')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="8" class="d-flex align-start">
              <v-btn
                size="small" variant="tonal" color="green-darken-2" prepend-icon="mdi-account-arrow-down"
                :disabled="!tournamentForm.chief_arbiter_name"
                @click="fillOrganizerFromChiefArbiter"
              >{{ t('trnreg.fill_as_chief_organizer') }}</v-btn>
            </v-col>

            <v-col cols="12" sm="8">
              <div class="trnreg-lookup-wrap">
                <v-text-field
                  v-model="arbiterLookup.deputy_arbiter_1.query"
                  :label="t('trnreg.field_deputy_arbiter_1_search')"
                  variant="outlined" color="green-darken-2" density="compact" autocomplete="off"
                  :hint="t('trnreg.lookup_hint')" persistent-hint
                  @input="onArbiterLookupInput('deputy_arbiter_1')"
                  @blur="hideArbiterLookupResults('deputy_arbiter_1')"
                ></v-text-field>
                <span v-if="arbiterLookup.deputy_arbiter_1.searching" class="trnreg-searching-hint">{{ t('trnreg.lookup_searching') }}</span>
                <ul v-if="arbiterLookup.deputy_arbiter_1.results.length" class="trnreg-dropdown">
                  <li v-for="p in arbiterLookup.deputy_arbiter_1.results" :key="p.fide_id || p.national_id || p.name" @mousedown.prevent="selectArbiterLookupResult('deputy_arbiter_1', p)">
                    {{ p.name }} <span class="trnreg-dropdown-meta">{{ p.fide_id || '' }} {{ p.club || '' }}</span>
                  </li>
                </ul>
                <div v-if="!arbiterLookup.deputy_arbiter_1.searching && arbiterLookup.deputy_arbiter_1.query.trim().length >= 2 && !arbiterLookup.deputy_arbiter_1.results.length" class="trnreg-searching-hint">{{ t('trnreg.lookup_no_results') }}</div>
              </div>
              <div class="text-body-2 mt-1">
                <template v-if="tournamentForm.deputy_arbiter_1_name || tournamentForm.deputy_arbiter_1_person_id">
                  {{ t('trnreg.selected_person') }}: <strong>{{ tournamentForm.deputy_arbiter_1_name }}</strong>
                  <span class="text-grey-darken-1">({{ t('trnreg.field_fide_id') }}: {{ tournamentForm.deputy_arbiter_1_person_id || t('trnreg.no_fide_id') }})</span>
                  <v-btn size="x-small" variant="text" color="red-darken-2" @click="clearArbiterSelection('deputy_arbiter_1')">{{ t('trnreg.clear_selection') }}</v-btn>
                </template>
                <span v-else class="text-grey-darken-1">{{ t('trnreg.no_person_selected') }}</span>
              </div>
            </v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.deputy_arbiter_1_email" :label="t('trnreg.field_deputy_arbiter_1_email')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>

            <v-col cols="12" sm="8">
              <div class="trnreg-lookup-wrap">
                <v-text-field
                  v-model="arbiterLookup.deputy_arbiter_2.query"
                  :label="t('trnreg.field_deputy_arbiter_2_search')"
                  variant="outlined" color="green-darken-2" density="compact" autocomplete="off"
                  :hint="t('trnreg.lookup_hint')" persistent-hint
                  @input="onArbiterLookupInput('deputy_arbiter_2')"
                  @blur="hideArbiterLookupResults('deputy_arbiter_2')"
                ></v-text-field>
                <span v-if="arbiterLookup.deputy_arbiter_2.searching" class="trnreg-searching-hint">{{ t('trnreg.lookup_searching') }}</span>
                <ul v-if="arbiterLookup.deputy_arbiter_2.results.length" class="trnreg-dropdown">
                  <li v-for="p in arbiterLookup.deputy_arbiter_2.results" :key="p.fide_id || p.national_id || p.name" @mousedown.prevent="selectArbiterLookupResult('deputy_arbiter_2', p)">
                    {{ p.name }} <span class="trnreg-dropdown-meta">{{ p.fide_id || '' }} {{ p.club || '' }}</span>
                  </li>
                </ul>
                <div v-if="!arbiterLookup.deputy_arbiter_2.searching && arbiterLookup.deputy_arbiter_2.query.trim().length >= 2 && !arbiterLookup.deputy_arbiter_2.results.length" class="trnreg-searching-hint">{{ t('trnreg.lookup_no_results') }}</div>
              </div>
              <div class="text-body-2 mt-1">
                <template v-if="tournamentForm.deputy_arbiter_2_name || tournamentForm.deputy_arbiter_2_person_id">
                  {{ t('trnreg.selected_person') }}: <strong>{{ tournamentForm.deputy_arbiter_2_name }}</strong>
                  <span class="text-grey-darken-1">({{ t('trnreg.field_fide_id') }}: {{ tournamentForm.deputy_arbiter_2_person_id || t('trnreg.no_fide_id') }})</span>
                  <v-btn size="x-small" variant="text" color="red-darken-2" @click="clearArbiterSelection('deputy_arbiter_2')">{{ t('trnreg.clear_selection') }}</v-btn>
                </template>
                <span v-else class="text-grey-darken-1">{{ t('trnreg.no_person_selected') }}</span>
              </div>
            </v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.deputy_arbiter_2_email" :label="t('trnreg.field_deputy_arbiter_2_email')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>

            <v-col cols="12"><div class="text-subtitle-2 font-weight-bold text-green-darken-3 mt-2">{{ t('trnreg.section_organizer') }}</div></v-col>
            <v-col cols="12" sm="6">
              <div class="trnreg-lookup-wrap">
                <v-text-field
                  v-model="arbiterLookup.chief_organizer.query"
                  :label="t('trnreg.field_chief_organizer_search')"
                  variant="outlined" color="green-darken-2" density="compact" autocomplete="off"
                  :hint="t('trnreg.lookup_hint')" persistent-hint
                  @input="onArbiterLookupInput('chief_organizer')"
                  @blur="hideArbiterLookupResults('chief_organizer')"
                ></v-text-field>
                <span v-if="arbiterLookup.chief_organizer.searching" class="trnreg-searching-hint">{{ t('trnreg.lookup_searching') }}</span>
                <ul v-if="arbiterLookup.chief_organizer.results.length" class="trnreg-dropdown">
                  <li v-for="p in arbiterLookup.chief_organizer.results" :key="p.fide_id || p.national_id || p.name" @mousedown.prevent="selectArbiterLookupResult('chief_organizer', p)">
                    {{ p.name }} <span class="trnreg-dropdown-meta">{{ p.fide_id || '' }} {{ p.club || '' }}</span>
                  </li>
                </ul>
                <div v-if="!arbiterLookup.chief_organizer.searching && arbiterLookup.chief_organizer.query.trim().length >= 2 && !arbiterLookup.chief_organizer.results.length" class="trnreg-searching-hint">{{ t('trnreg.lookup_no_results') }}</div>
              </div>
              <div class="text-body-2 mt-1">
                <template v-if="tournamentForm.chief_organizer_name || tournamentForm.chief_organizer_person_id">
                  {{ t('trnreg.selected_person') }}: <strong>{{ tournamentForm.chief_organizer_name }}</strong>
                  <span class="text-grey-darken-1">({{ t('trnreg.field_fide_id') }}: {{ tournamentForm.chief_organizer_person_id || t('trnreg.no_fide_id') }})</span>
                  <v-btn size="x-small" variant="text" color="red-darken-2" @click="clearArbiterSelection('chief_organizer')">{{ t('trnreg.clear_selection') }}</v-btn>
                </template>
                <span v-else class="text-grey-darken-1">{{ t('trnreg.no_person_selected') }}</span>
              </div>
            </v-col>
            <v-col cols="12" sm="3"><v-text-field v-model="tournamentForm.chief_organizer_email" :label="t('trnreg.field_chief_organizer_email')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="3"><v-text-field v-model="tournamentForm.chief_organizer_phone" :label="t('trnreg.field_chief_organizer_phone')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>

            <v-col cols="12"><div class="text-subtitle-2 font-weight-bold text-green-darken-3 mt-2">{{ t('trnreg.section_email_copies') }}</div></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.email_copy_1" :label="t('trnreg.field_email_copy_1')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.email_copy_2" :label="t('trnreg.field_email_copy_2')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.email_copy_3" :label="t('trnreg.field_email_copy_3')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeTournamentForm">{{ t('trnreg.cancel_btn') }}</v-btn>
          <v-btn color="green-darken-2" :loading="tournamentSubmitting" @click="saveTournament">{{ t('trnreg.save_btn') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="deleteTournamentDialog" max-width="480">
      <v-card v-if="deleteTournamentTarget">
        <v-card-title class="text-red-darken-2">{{ t('trnreg.admin_delete_tournament_title') }}</v-card-title>
        <v-card-text>
          <p>{{ t('trnreg.admin_delete_tournament_warning') }}</p>
          <p class="font-weight-bold text-body-1 my-2">{{ deleteTournamentTarget.name }}</p>
          <v-alert v-if="deleteTournamentError" type="error" class="mb-3">{{ deleteTournamentError }}</v-alert>
          <v-text-field
            v-model="deleteTournamentConfirmText"
            :label="t('trnreg.admin_delete_tournament_type_name')"
            variant="outlined" color="red-darken-2" density="compact" autocomplete="off"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeDeleteTournament">{{ t('trnreg.cancel_btn') }}</v-btn>
          <v-btn
            color="red-darken-2"
            :disabled="deleteTournamentConfirmText !== deleteTournamentTarget.name"
            :loading="deleteTournamentSubmitting"
            @click="confirmDeleteTournament"
          >{{ t('trnreg.admin_delete_tournament_confirm_btn') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.trnreg-shell {
  max-width: 1100px;
}
/* A required field's label prints its name in bold rather than relying on
   Vuetify's asterisk alone, which is easy to miss on a compact-density
   field. */
.trnreg-required :deep(.v-label) {
  font-weight: 700;
}
.border-green {
  border-left: 5px solid #1b5e20 !important;
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
.trnreg-success-check {
  width: 72px;
  height: 72px;
  margin: 0 auto;
  background-color: #2e7d32;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.4rem;
  box-shadow: 0 10px 25px rgba(46, 125, 50, 0.3);
}
.trnreg-table-scroll {
  overflow-x: auto;
}
</style>

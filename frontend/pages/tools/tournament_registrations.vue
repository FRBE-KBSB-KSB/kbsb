<script setup>
import { ref, computed, onMounted } from "vue"
import { useRoute } from "vue-router"
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
  affiliated: false,
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
}

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
const view = ref("form")
const trnId = computed(() => route.query.trn || null)

const tournament = ref(null)
const loadingTournament = ref(false)
const errorText = ref("")

const adminName = ref("")

function setLocale(l) {
  locale.value = l
}

function goToForm() {
  view.value = "form"
  if (!tournament.value) loadTournament()
}
function goToList() {
  view.value = "list"
  loadRegistrations()
}
function goToLogin() {
  view.value = "login"
}
function goToAdmin() {
  view.value = "admin"
  if (!adminTournaments.value.length) loadAdminTournaments()
}

function logout() {
  tokenStore.updateToken(null)
  adminName.value = ""
  if (typeof window !== "undefined") window.localStorage.removeItem("tournamentregname")
  selectedAdminTournament.value = null
  adminRegistrations.value = []
  adminTournaments.value = []
  view.value = trnId.value ? "form" : "login"
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
  } catch (error) {
    tournament.value = null
    errorText.value = error.code === 404 ? t("trnreg.tournament_not_found") : t("trnreg.load_tournament_failed")
  } finally {
    loadingTournament.value = false
  }
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

function cleanTournamentPayload(form, obligatoryPresenceTimeValue) {
  const payload = { ...form }
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
    payload.obligatory_presence = localDateTimeToUtcIso(form.date_start, obligatoryPresenceTimeValue)
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
  target.affiliated = !!p.affiliated
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
const regSubmitting = ref(false)
const regError = ref("")
const submittedRegistration = ref(null)

async function submitRegistration() {
  regSubmitting.value = true
  regError.value = ""
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
const listSortKey = ref("id")
const listSortOrder = ref("asc")

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

function sortCompare(a, b, key, mult) {
  let valA = a[key]
  let valB = b[key]
  if (key === "category_index" || key === "fide_rating_standard" || key === "id") {
    valA = Number(valA) || 0
    valB = Number(valB) || 0
  } else {
    valA = valA ? String(valA).toLowerCase() : ""
    valB = valB ? String(valB).toLowerCase() : ""
  }
  if (valA < valB) return -1 * mult
  if (valA > valB) return 1 * mult
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
  return [...filteredRegistrations.value].sort((a, b) => sortCompare(a, b, listSortKey.value, mult))
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

function formatDateDisplay(iso) {
  if (!iso) return ""
  const m = String(iso).match(/^(\d{4})-(\d{2})-(\d{2})/)
  return m ? `${m[3]}/${m[2]}/${m[1]}` : String(iso)
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

function openEditRegistration(row, isAdmin) {
  editRegId.value = row.id
  editRegIsAdmin.value = isAdmin
  editRegForm.value = { ...EMPTY_REGISTRATION, ...row }
  editRegLookupQuery.value = ""
  editRegLookupResults.value = []
  editRegError.value = ""
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
    if (editRegIsAdmin.value) {
      await $backend("tournament_registrations", "admin_updateRegistration", {
        id: editRegId.value,
        token: token.value,
        ...cleanRegistrationPayload(editRegForm.value),
      })
    } else {
      await $backend("tournament_registrations", "updateRegistration", {
        id: editRegId.value,
        ...cleanRegistrationPayload(editRegForm.value),
      })
    }
    editRegDialog.value = false
    if (editRegIsAdmin.value) {
      await loadAdminRegistrations()
    } else {
      await loadRegistrations()
    }
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
    loadAdminTournaments()
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
  return [...adminRegistrations.value].sort((a, b) => sortCompare(a, b, adminListSortKey.value, mult))
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
function publicTournamentUrl(trn) {
  return `${route.path}?trn=${encodeURIComponent(trn.id)}`
}

function openPublicTournamentPage(trn) {
  if (typeof window !== "undefined") window.open(publicTournamentUrl(trn), "_blank", "noopener")
}

async function loadAdminRegistrations() {
  if (!selectedAdminTournament.value) return
  loadingAdminRegistrations.value = true
  try {
    const reply = await $backend("tournament_registrations", "getRegistrations", { id: selectedAdminTournament.value.id })
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

// Combines a bare "YYYY-MM-DD" date with a bare "HH:MM" time into a real
// UTC instant (proper ISO string, not a naive offset-less concatenation)
// before it goes over the wire. The old version just concatenated the two
// strings with no offset at all, which is genuinely ambiguous -- Postgres
// interprets an offset-less timestamp according to whatever timezone the
// session happens to be configured with, not necessarily what the arbiter
// actually typed, and it silently "round-tripped" back out looking
// unchanged because every reader (this page's old extractTimeHHMM, the
// confirmation email's old UTC-getter-based formatter) was making the same
// unstated assumption. Building a real local Date and letting the browser
// convert it removes the ambiguity entirely. Assumes the person running
// this admin panel is physically in Belgium -- the same assumption a bare
// <input type="time"> already makes implicitly, since it has no timezone
// concept of its own either.
function localDateTimeToUtcIso(dateStr, timeStr) {
  const [y, mo, d] = dateStr.split("-").map(Number)
  const [h, mi] = timeStr.split(":").map(Number)
  return new Date(y, mo - 1, d, h, mi, 0).toISOString()
}

// Inverse of the above: given a stored UTC instant, returns the browser-
// local "HH:MM" -- used both to prefill the edit form's time input and to
// display the value on the dashboard (see formatObligatoryPresence below).
function utcIsoToLocalHHMM(value) {
  if (!value) return ""
  const dt = new Date(value)
  if (isNaN(dt.getTime())) return ""
  const pad = (n) => String(n).padStart(2, "0")
  return `${pad(dt.getHours())}:${pad(dt.getMinutes())}`
}

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
  tournamentForm.value = { ...EMPTY_TOURNAMENT, categories: [] }
  obligatoryPresenceTime.value = ""
  resetArbiterLookupState()
  tournamentFormError.value = ""
  tournamentFormDialog.value = true
}

function openEditTournament(trn) {
  tournamentFormMode.value = "edit"
  tournamentForm.value = { ...EMPTY_TOURNAMENT, ...trn, categories: Array.isArray(trn.categories) ? [...trn.categories] : [] }
  obligatoryPresenceTime.value = utcIsoToLocalHHMM(trn.obligatory_presence)
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

function addCategoryRow() {
  tournamentForm.value.categories.push("")
}
function removeCategoryRow(i) {
  tournamentForm.value.categories.splice(i, 1)
}

async function saveTournament() {
  tournamentSubmitting.value = true
  tournamentFormError.value = ""
  adminActionNotice.value = ""
  try {
    const categories = tournamentForm.value.categories.filter((c) => c && c.trim())
    const payload = { ...cleanTournamentPayload(tournamentForm.value, obligatoryPresenceTime.value), categories }
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

const exportingCsv = ref(false)
const exportingSwar = ref({ a: false, b: false, c: false })
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

async function exportCsv() {
  if (!selectedAdminTournament.value) return
  exportingCsv.value = true
  adminActionError.value = ""
  try {
    const reply = await $backend("tournament_registrations", "admin_exportCsv", {
      id: selectedAdminTournament.value.id,
      token: token.value,
    })
    triggerDownload(reply.data, `registrations_${selectedAdminTournament.value.id}.csv`)
  } catch (error) {
    adminActionError.value = t("trnreg.admin_export_failed")
  } finally {
    exportingCsv.value = false
  }
}

async function exportSwar(category) {
  if (!selectedAdminTournament.value) return
  exportingSwar.value = { ...exportingSwar.value, [category]: true }
  adminActionError.value = ""
  try {
    const reply = await $backend("tournament_registrations", "admin_exportSwar", {
      id: selectedAdminTournament.value.id,
      category,
      token: token.value,
    })
    triggerDownload(reply.data, `swar_${category}_${selectedAdminTournament.value.id}.csv`)
  } catch (error) {
    adminActionError.value = t("trnreg.admin_export_failed")
  } finally {
    exportingSwar.value = { ...exportingSwar.value, [category]: false }
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
    // ?view=list is a direct deep link to the public listing (used by the
    // confirmation email's "list of registrations" link, mirroring the
    // legacy tool's own separate listingRegistrations.php?trn=... page) --
    // any other/missing value keeps the existing default of landing on the
    // registration form.
    view.value = route.query.view === "list" ? "list" : "form"
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
      <v-col cols="auto" v-if="trnId && view !== 'form'">
        <v-btn size="small" variant="tonal" color="green-darken-2" prepend-icon="mdi-arrow-left" @click="goToForm">{{ t('trnreg.nav_back_to_form') }}</v-btn>
      </v-col>
      <v-col cols="auto" v-if="trnId && view === 'form'">
        <v-btn size="small" variant="text" color="green-darken-2" prepend-icon="mdi-format-list-bulleted" @click="goToList">{{ t('trnreg.nav_list') }}</v-btn>
      </v-col>
      <v-col cols="auto" v-if="trnId && view === 'list'">
        <v-btn size="small" variant="text" color="green-darken-2" prepend-icon="mdi-account-edit" @click="goToForm">{{ t('trnreg.nav_form') }}</v-btn>
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

    <!-- ============ VIEW: public registration form ============ -->
    <div v-if="view === 'form'">
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
                <strong>{{ t('trnreg.th_time_control') }}:</strong> {{ tournament.time_control }}<span v-if="tournament.time_control_details"> ({{ tournament.time_control_details }})</span>
              </v-col>
              <v-col cols="12" sm="6" md="4" v-if="tournament.closing_registrations">
                <strong>{{ t('trnreg.th_closing') }}:</strong> {{ formatDateDisplay(tournament.closing_registrations) }}
              </v-col>
              <v-col cols="12" sm="6" md="4" v-if="tournament.obligatory_presence">
                <strong>{{ t('trnreg.th_obligatory_presence') }}:</strong> {{ utcIsoToLocalHHMM(tournament.obligatory_presence) }}
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

        <div v-if="tournament">
          <v-card v-if="submittedRegistration" class="elevation-2">
            <v-card-text class="text-center py-8">
              <div class="trnreg-success-check">&#10003;</div>
              <h2 class="text-h6 font-weight-bold mt-4 mb-2">{{ t('trnreg.submitted_title') }}</h2>
              <p class="text-body-2 mb-3">{{ t('trnreg.submitted_msg') }}</p>
              <p class="text-h6 font-weight-bold text-green-darken-3">{{ t('trnreg.registration_id_label') }}: {{ submittedRegistration.id }}</p>
              <v-btn color="green-darken-2" class="mt-3" @click="resetRegForm">{{ t('trnreg.register_another') }}</v-btn>
            </v-card-text>
          </v-card>

          <v-card v-else class="elevation-2">
            <v-card-text>
              <v-alert v-if="regError" type="error" class="mb-4">{{ regError }}</v-alert>
              <v-form @submit.prevent="submitRegistration">
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
                    <v-text-field v-model="regForm.last_name" :label="t('trnreg.field_last_name')" variant="outlined" color="green-darken-2" density="compact" required></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-text-field v-model="regForm.first_name" :label="t('trnreg.field_first_name')" variant="outlined" color="green-darken-2" density="compact" required></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-select v-model="regForm.sex" :items="[{ title: t('trnreg.sex_m'), value: 'M' }, { title: t('trnreg.sex_f'), value: 'F' }]" item-title="title" item-value="value" :label="t('trnreg.field_sex')" variant="outlined" color="green-darken-2" density="compact"></v-select>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.date_birth" type="date" :label="t('trnreg.field_date_birth')" variant="outlined" color="green-darken-2" density="compact" required :hint="matchedBirthYear ? (t('trnreg.birth_year_hint') + ': ' + matchedBirthYear) : ''" persistent-hint></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.place_birth" :label="t('trnreg.field_place_birth')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-text-field v-model="regForm.country_residence" :label="t('trnreg.field_country_residence')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-text-field v-model="regForm.nationality" :label="t('trnreg.field_nationality')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.phone" :label="t('trnreg.field_phone')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.gsm" :label="t('trnreg.field_gsm')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.email" type="email" :label="t('trnreg.field_email')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.national_id" :label="t('trnreg.field_national_id')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.national_club" :label="t('trnreg.field_national_club')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4" class="d-flex align-center">
                    <v-checkbox v-model="regForm.affiliated" :label="t('trnreg.field_affiliated')" color="green-darken-2" density="compact" hide-details></v-checkbox>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.fide_id" :label="t('trnreg.field_fide_id')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.fide_title" :label="t('trnreg.field_fide_title')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.fide_federation" :label="t('trnreg.field_fide_federation')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.fide_rating_standard" type="number" :label="t('trnreg.field_fide_rating_standard')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.fide_rating_rapid" type="number" :label="t('trnreg.field_fide_rating_rapid')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="regForm.fide_rating_blitz" type="number" :label="t('trnreg.field_fide_rating_blitz')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-select
                      v-model="regForm.category_index"
                      :items="(tournament.categories || []).map((c, i) => ({ title: c, value: i }))"
                      :label="t('trnreg.field_category')"
                      :placeholder="t('trnreg.category_placeholder')"
                      variant="outlined" color="green-darken-2" density="compact"
                    ></v-select>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-text-field v-model="regForm.rounds_absent" :label="t('trnreg.field_rounds_absent')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-text-field v-model="regForm.contact" :label="t('trnreg.field_contact')" variant="outlined" color="green-darken-2" density="compact"></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6" class="d-flex align-center">
                    <v-checkbox v-model="regForm.g_license" :label="t('trnreg.field_g_license')" color="green-darken-2" density="compact" hide-details></v-checkbox>
                  </v-col>
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
                  <th style="cursor:pointer;user-select:none;" @click="toggleListSort('id')">{{ t('trnreg.col_id') }} <v-icon size="small">{{ listSortKey === 'id' ? (listSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}</v-icon></th>
                  <th style="cursor:pointer;user-select:none;" @click="toggleListSort('last_name')">{{ t('trnreg.col_name') }} <v-icon size="small">{{ listSortKey === 'last_name' ? (listSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}</v-icon></th>
                  <th style="cursor:pointer;user-select:none;" @click="toggleListSort('sex')">{{ t('trnreg.col_sex') }}</th>
                  <th style="cursor:pointer;user-select:none;" @click="toggleListSort('date_birth')">{{ t('trnreg.col_birth') }} <v-icon size="small">{{ listSortKey === 'date_birth' ? (listSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}</v-icon></th>
                  <th style="cursor:pointer;user-select:none;" @click="toggleListSort('national_club')">{{ t('trnreg.col_club') }}</th>
                  <th>{{ t('trnreg.col_category') }}</th>
                  <th style="cursor:pointer;user-select:none;" @click="toggleListSort('fide_id')">{{ t('trnreg.col_fide_id') }}</th>
                  <th style="cursor:pointer;user-select:none;" @click="toggleListSort('fide_rating_standard')">{{ t('trnreg.col_rating') }} <v-icon size="small">{{ listSortKey === 'fide_rating_standard' ? (listSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}</v-icon></th>
                  <th>{{ t('trnreg.col_actions') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in sortedRegistrations" :key="r.id">
                  <td>{{ r.id }}</td>
                  <td>{{ r.last_name }} {{ r.first_name }}</td>
                  <td>{{ r.sex }}</td>
                  <td>{{ formatDateDisplay(r.date_birth) }}</td>
                  <td>{{ r.national_club_name || r.national_club }}</td>
                  <td>{{ categoryLabel(tournament, r.category_index) }}</td>
                  <td>{{ r.fide_id }}</td>
                  <td>{{ r.fide_rating_standard }}</td>
                  <td>
                    <v-btn size="small" variant="text" color="green-darken-2" @click="openEditRegistration(r, false)">{{ t('trnreg.edit_btn') }}</v-btn>
                  </td>
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
          <v-form @submit.prevent="submitLogin">
            <v-text-field v-model="loginUsername" :label="t('trnreg.field_username')" variant="outlined" color="green-darken-2" density="comfortable" autocomplete="username" required></v-text-field>
            <v-text-field v-model="loginPassword" type="password" :label="t('trnreg.field_password')" variant="outlined" color="green-darken-2" density="comfortable" autocomplete="current-password" required></v-text-field>
            <v-btn type="submit" color="green-darken-2" block :loading="loginSubmitting">{{ t('trnreg.login_btn') }}</v-btn>
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
        <v-row v-else dense>
          <v-col cols="12" md="6" lg="4" v-for="trn in adminTournaments" :key="trn.id">
            <v-card class="elevation-2 h-100">
              <v-card-text>
                <h3 class="text-subtitle-1 font-weight-bold text-green-darken-3">{{ trn.name }}</h3>
                <div class="text-body-2 text-grey-darken-2">
                  {{ formatDateDisplay(trn.date_start) }}<span v-if="trn.date_end && trn.date_end !== trn.date_start"> - {{ formatDateDisplay(trn.date_end) }}</span>
                </div>
                <div class="text-body-2 text-grey-darken-2" v-if="trn.city">{{ trn.city }}</div>
                <div class="d-flex flex-wrap ga-2 mt-3">
                  <v-btn size="small" color="green-darken-2" variant="tonal" @click="selectAdminTournament(trn)">{{ t('trnreg.admin_manage_registrations') }}</v-btn>
                  <v-btn size="small" variant="text" color="grey-darken-1" @click="openEditTournament(trn)">{{ t('trnreg.admin_edit_tournament') }}</v-btn>
                  <v-btn size="small" variant="text" color="green-darken-2" prepend-icon="mdi-open-in-new" @click="openPublicTournamentPage(trn)">{{ t('trnreg.admin_view_public_page') }}</v-btn>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
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
                <v-btn size="small" variant="text" color="green-darken-2" prepend-icon="mdi-open-in-new" @click="openPublicTournamentPage(selectedAdminTournament)">{{ t('trnreg.admin_view_public_page') }}</v-btn>
                <v-btn size="small" variant="text" color="red-darken-2" prepend-icon="mdi-delete" @click="openDeleteTournament(selectedAdminTournament)">{{ t('trnreg.admin_delete_tournament') }}</v-btn>
                <v-btn size="small" variant="tonal" color="green-darken-2" prepend-icon="mdi-download" :loading="exportingCsv" @click="exportCsv">{{ t('trnreg.admin_export_csv') }}</v-btn>
                <v-btn size="small" variant="tonal" color="green-darken-2" :loading="exportingSwar.a" @click="exportSwar('a')">{{ t('trnreg.admin_export_swar_a') }}</v-btn>
                <v-btn size="small" variant="tonal" color="green-darken-2" :loading="exportingSwar.b" @click="exportSwar('b')">{{ t('trnreg.admin_export_swar_b') }}</v-btn>
                <v-btn size="small" variant="tonal" color="green-darken-2" :loading="exportingSwar.c" @click="exportSwar('c')">{{ t('trnreg.admin_export_swar_c') }}</v-btn>
                <v-btn size="small" variant="tonal" color="blue-darken-2" prepend-icon="mdi-refresh" :loading="refreshEloLoading" @click="refreshElo">{{ t('trnreg.admin_refresh_elo') }}</v-btn>
              </v-col>
            </v-row>
            <v-alert v-if="refreshEloResult !== null" type="success" density="compact" class="mt-3">
              {{ t('trnreg.admin_refresh_elo_result').replace('{count}', refreshEloResult) }}
            </v-alert>
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
                    <th style="cursor:pointer;user-select:none;" @click="toggleAdminListSort('fide_rating_standard')">{{ t('trnreg.col_rating') }} <v-icon size="small">{{ adminListSortKey === 'fide_rating_standard' ? (adminListSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}</v-icon></th>
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
                    <td>{{ r.fide_rating_standard }}</td>
                    <td>{{ r.email }}</td>
                    <td>{{ r.phone || r.gsm }}</td>
                    <td class="text-no-wrap">
                      <v-btn size="small" variant="text" color="green-darken-2" @click="openEditRegistration(r, true)">{{ t('trnreg.edit_btn') }}</v-btn>
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
            <v-col cols="12" sm="6"><v-text-field v-model="editRegForm.last_name" :label="t('trnreg.field_last_name')" variant="outlined" color="green-darken-2" density="compact" required></v-text-field></v-col>
            <v-col cols="12" sm="6"><v-text-field v-model="editRegForm.first_name" :label="t('trnreg.field_first_name')" variant="outlined" color="green-darken-2" density="compact" required></v-text-field></v-col>
            <v-col cols="12" sm="4">
              <v-select v-model="editRegForm.sex" :items="[{ title: t('trnreg.sex_m'), value: 'M' }, { title: t('trnreg.sex_f'), value: 'F' }]" item-title="title" item-value="value" :label="t('trnreg.field_sex')" variant="outlined" color="green-darken-2" density="compact"></v-select>
            </v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="editRegForm.date_birth" type="date" :label="t('trnreg.field_date_birth')" variant="outlined" color="green-darken-2" density="compact" required></v-text-field></v-col>
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
            <v-col cols="12" sm="6"><v-text-field v-model="editRegForm.contact" :label="t('trnreg.field_contact')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
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
            <v-col cols="12" sm="8"><v-text-field v-model="tournamentForm.name" :label="t('trnreg.field_name')" variant="outlined" color="green-darken-2" density="compact" required></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.city" :label="t('trnreg.field_city')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12"><v-text-field v-model="tournamentForm.address" :label="t('trnreg.field_address')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>

            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.date_start" type="date" :label="t('trnreg.field_date_start')" variant="outlined" color="green-darken-2" density="compact" required></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.date_end" type="date" :label="t('trnreg.field_date_end')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="obligatoryPresenceTime" type="time" :label="t('trnreg.field_obligatory_presence')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>

            <v-col cols="12" sm="6"><v-text-field v-model="tournamentForm.opening_registrations" type="date" :label="t('trnreg.field_opening_registrations')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="6"><v-text-field v-model="tournamentForm.closing_registrations" type="date" :label="t('trnreg.field_closing_registrations')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>

            <v-col cols="12" sm="4">
              <v-select v-model="tournamentForm.system" :items="SYSTEM_OPTIONS.map((s) => ({ title: t('trnreg.system_' + s), value: s }))" :label="t('trnreg.field_system')" variant="outlined" color="green-darken-2" density="compact"></v-select>
            </v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.rounds" type="number" :label="t('trnreg.field_rounds')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4">
              <v-select v-model="tournamentForm.time_control" :items="TIME_CONTROL_OPTIONS.map((s) => ({ title: t('trnreg.tc_' + s), value: s }))" :label="t('trnreg.field_time_control')" variant="outlined" color="green-darken-2" density="compact"></v-select>
            </v-col>
            <v-col cols="12"><v-text-field v-model="tournamentForm.time_control_details" :label="t('trnreg.field_time_control_details')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>

            <v-col cols="12">
              <div class="text-body-2 font-weight-bold mb-1">{{ t('trnreg.field_categories') }}</div>
              <div v-for="(c, i) in tournamentForm.categories" :key="i" class="d-flex align-center ga-2 mb-2">
                <v-text-field v-model="tournamentForm.categories[i]" density="compact" variant="outlined" color="green-darken-2" hide-details></v-text-field>
                <v-btn icon size="small" variant="text" color="red-darken-2" @click="removeCategoryRow(i)"><v-icon>mdi-close</v-icon></v-btn>
              </div>
              <v-btn size="small" variant="text" color="green-darken-2" prepend-icon="mdi-plus" @click="addCategoryRow">{{ t('trnreg.add_category') }}</v-btn>
            </v-col>

            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.url" :label="t('trnreg.field_url')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.organizing_club" :label="t('trnreg.field_organizing_club')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.federation" :label="t('trnreg.field_federation')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>

            <v-col cols="12" sm="4">
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
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.event_code_fide_a" :label="t('trnreg.field_event_code_fide_a')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.event_code_fide_b" :label="t('trnreg.field_event_code_fide_b')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>
            <v-col cols="12" sm="4"><v-text-field v-model="tournamentForm.event_code_fide_c" :label="t('trnreg.field_event_code_fide_c')" variant="outlined" color="green-darken-2" density="compact"></v-text-field></v-col>

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

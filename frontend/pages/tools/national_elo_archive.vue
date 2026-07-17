<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue"
import { useRoute } from "vue-router"
import { useI18n } from "vue-i18n"

const { t, locale } = useI18n()
const route = useRoute()
const { $backend } = useNuxtApp()

definePageMeta({
  layout: "nomenu",
})

// Search Mode ('player', 'club', or 'region')
const searchMode = ref("player")

// Player search state
const searchQuery = ref("")
const searching = ref(false)
const players = ref([])
const hasSearched = ref(false)
const errorText = ref("")

// Club search state
const clubSearchQuery = ref("")
const searchingClubs = ref(false)
const clubs = ref([])
const hasSearchedClubs = ref(false)
const selectedClub = ref(null)
const clubPlayers = ref([])
const loadingClubPlayers = ref(false)

// Selected profile state
const selectedPlayer = ref(null)
const profileLoading = ref(false)
const ratings = ref([])
const games = ref([])
const filteredPeriod = ref("All")
const totalGames = ref(0)
const latestGameDate = ref(null)

// Sorting states
const searchSortKey = ref('name')
const searchSortOrder = ref('asc')

const clubSortKey = ref('latest_elo')
const clubSortOrder = ref('desc')

const gamesSortKey = ref('date')
const gamesSortOrder = ref('desc')

// Hovered chart point state
const hoveredPoint = ref(null)

// Regions state
const loadingRegions = ref(false)
const regionsClubs = ref({})
const regionsList = [
  { id: 0, name: "Brussel / Bruxelles (VSF)", clubIds: [201, 204, 209, 229, 244] },
  { id: 100, name: "Antwerpen", clubIds: [108, 109, 114, 121, 124, 128, 130, 132, 134, 135, 143, 162, 166, 174, 176, 182, 188, 190, 194, 195, 196] },
  { id: 200, name: "Vlaams-Brabant", clubIds: [228, 230, 231, 233, 234, 235, 236, 238, 240, 260, 261] },
  { id: 299, name: "Bruxelles / Brussel (FEFB)", clubIds: [202, 207, 226, 239, 278, 289] },
  { id: 300, name: "West-Vlaanderen", clubIds: [301, 302, 303, 304, 305, 307, 309, 312, 313, 318, 322, 340, 351, 352, 353, 362, 363, 364] },
  { id: 400, name: "Oost-Vlaanderen", clubIds: [401, 402, 404, 408, 410, 417, 418, 422, 425, 430, 432, 436, 438, 460, 462, 465, 471, 472, 475] },
  { id: 500, name: "Hainaut", clubIds: [501, 511, 514, 520, 521, 525, 541, 547, 548, 549, 551] },
  { id: 600, name: "Liège", clubIds: [601, 603, 609, 618, 619, 621, 622, 641, 666] },
  { id: 699, name: "SVDB", clubIds: [604, 607, 623, 627] },
  { id: 700, name: "Limburg", clubIds: [701, 703, 705, 707, 708, 712, 713, 714, 715, 725, 726, 727, 732, 733, 736, 737, 741, 742, 743] },
  { id: 800, name: "Namur - Luxembourg", clubIds: [810, 811, 814, 816] },
  { id: 900, name: "Namur", clubIds: [901, 902, 906, 909] },
  { id: 950, name: "Brabant Wallon", clubIds: [518, 951, 952, 953, 954, 961, 962] }
]

async function loadAllClubsForRegions() {
  loadingRegions.value = true
  errorText.value = ""
  regionsClubs.value = {}
  
  try {
    const res = await $backend("national_elo_archive", "getAllClubs")
    if (res && res.data && res.data.success) {
      const clubsList = res.data.clubs || []
      
      const grouped = {}
      regionsList.forEach(r => {
        grouped[r.id] = []
      })
      
      clubsList.forEach(club => {
        if (!club.player_count || club.player_count === 0) return
        
        const region = regionsList.find(r => r.clubIds.includes(club.club_id))
        if (region) {
          grouped[region.id].push(club)
        }
      })
      
      regionsClubs.value = grouped
    } else {
      errorText.value = "Failed to load clubs for regions"
    }
  } catch (error) {
    console.error(error)
    errorText.value = error.message || "An error occurred fetching regions clubs"
  } finally {
    loadingRegions.value = false
  }
}

watch(searchMode, (newVal) => {
  if (newVal === "region" && Object.keys(regionsClubs.value).length === 0) {
    loadAllClubsForRegions()
  }
})

// API methods
async function handleSearch() {
  if (!searchQuery.value || searchQuery.value.trim().length < 2) return
  searching.value = true
  hasSearched.value = true
  errorText.value = ""
  players.value = []
  
  try {
    const res = await $backend("national_elo_archive", "search", { q: searchQuery.value })
    if (res && res.data && res.data.success) {
      players.value = res.data.players
    } else {
      errorText.value = "Failed to load players"
    }
  } catch (error) {
    console.error(error)
    errorText.value = error.message || "An error occurred during search"
  } finally {
    searching.value = false
  }
}

async function handleClubSearch() {
  if (!clubSearchQuery.value || clubSearchQuery.value.trim().length < 2) return
  searchingClubs.value = true
  hasSearchedClubs.value = true
  errorText.value = ""
  clubs.value = []
  selectedClub.value = null
  
  try {
    const res = await $backend("national_elo_archive", "searchClubs", { q: clubSearchQuery.value })
    if (res && res.data && res.data.success) {
      clubs.value = res.data.clubs
    } else {
      errorText.value = "Failed to load clubs"
    }
  } catch (error) {
    console.error(error)
    errorText.value = error.message || "An error occurred during club search"
  } finally {
    searchingClubs.value = false
  }
}

async function selectClub(club) {
  selectedClub.value = club
  loadingClubPlayers.value = true
  errorText.value = ""
  clubPlayers.value = []
  
  try {
    const res = await $backend("national_elo_archive", "getClubPlayers", { club_id: club.club_id })
    if (res && res.data && res.data.success) {
      clubPlayers.value = res.data.players
    } else {
      errorText.value = "Failed to load club players"
    }
  } catch (error) {
    console.error(error)
    errorText.value = error.message || "An error occurred fetching club players"
  } finally {
    loadingClubPlayers.value = false
  }
}

async function selectPlayer(memberId) {
  profileLoading.value = true
  errorText.value = ""
  ratings.value = []
  games.value = []
  filteredPeriod.value = "All"
  hoveredPoint.value = null
  totalGames.value = 0
  latestGameDate.value = null
  
  try {
    const res = await $backend("national_elo_archive", "getProfile", { member_id: memberId })
    if (res && res.data && res.data.success) {
      selectedPlayer.value = res.data.player
      ratings.value = res.data.ratings
      games.value = res.data.games
      totalGames.value = res.data.total_games || 0
      latestGameDate.value = res.data.latest_game_date || null
    } else {
      errorText.value = "Failed to load player profile"
    }
  } catch (error) {
    console.error(error)
    errorText.value = error.message || "An error occurred fetching player details"
  } finally {
    profileLoading.value = false
  }
}

// Sorting helpers and computed properties
function sortCompare(a, b, key, orderMultiplier) {
  let valA = a[key]
  let valB = b[key]
  
  if (key === 'latest_elo' || key === 'opponent_elo' || key === 'member_id' || key === 'club_id' || key === 'player_count') {
    valA = Number(valA) || 0
    valB = Number(valB) || 0
  } else {
    valA = valA ? String(valA).toLowerCase() : ""
    valB = valB ? String(valB).toLowerCase() : ""
  }
  
  if (valA === valB) return 0
  if (valA === "" || valA === 0) return 1
  if (valB === "" || valB === 0) return -1
  
  if (typeof valA === 'number') {
    return (valA - valB) * orderMultiplier
  }
  return valA.localeCompare(valB) * orderMultiplier
}

const sortedPlayers = computed(() => {
  const key = searchSortKey.value
  const mult = searchSortOrder.value === 'asc' ? 1 : -1
  return [...players.value].sort((a, b) => sortCompare(a, b, key, mult))
})

const sortedClubPlayers = computed(() => {
  const key = clubSortKey.value
  const mult = clubSortOrder.value === 'asc' ? 1 : -1
  return [...clubPlayers.value].sort((a, b) => sortCompare(a, b, key, mult))
})

const sortedGames = computed(() => {
  const key = gamesSortKey.value
  const mult = gamesSortOrder.value === 'asc' ? 1 : -1
  return [...filteredGames.value].sort((a, b) => sortCompare(a, b, key, mult))
})

function toggleSortSearch(key) {
  if (searchSortKey.value === key) {
    searchSortOrder.value = searchSortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    searchSortKey.value = key
    searchSortOrder.value = 'asc'
  }
}

function toggleSortClub(key) {
  if (clubSortKey.value === key) {
    clubSortOrder.value = clubSortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    clubSortKey.value = key
    clubSortOrder.value = 'asc'
  }
}

function toggleSortGames(key) {
  if (gamesSortKey.value === key) {
    gamesSortOrder.value = gamesSortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    gamesSortKey.value = key
    gamesSortOrder.value = 'asc'
  }
}

// Periods filter options
const periodsList = computed(() => {
  const periods = new Set(games.value.map(g => g.period))
  return ["All", ...Array.from(periods).sort().reverse()]
})

// Filtered games list
const filteredGames = computed(() => {
  if (filteredPeriod.value === "All") {
    return games.value
  }
  return games.value.filter(g => g.period === filteredPeriod.value)
})

const latestPeriod = computed(() => {
  if (ratings.value && ratings.value.length > 0) {
    return ratings.value[ratings.value.length - 1].period
  }
  if (clubPlayers.value && clubPlayers.value.length > 0) {
    return clubPlayers.value[0].latest_elo_period
  }
  if (players.value && players.value.length > 0) {
    return players.value[0].latest_elo_period
  }
  return null
})

function goToClub(club) {
  selectedPlayer.value = null
  searchMode.value = 'club'
  selectClub(club)
}

function getPlayerResultText(game) {
  if (game.result === '1/2') return '½'
  const isWhite = game.color === 'W'
  if (game.result === '1-0') return isWhite ? '1' : '0'
  if (game.result === '0-1') return isWhite ? '0' : '1'
  return game.result
}

function getPlayerResultColor(game) {
  const res = getPlayerResultText(game)
  if (res === '1') return 'green-darken-1'
  if (res === '½') return 'grey-darken-1'
  if (res === '0') return 'red-darken-1'
  return 'grey'
}

function getEloChange(game) {
  if (!game.k_factor) return '-'
  let score = 0
  if (game.result === '1-0') score = game.color === 'W' ? 1.0 : 0.0
  else if (game.result === '0-1') score = game.color === 'W' ? 0.0 : 1.0
  else if (game.result === '1/2') score = 0.5
  
  const we = (game.expected_score || 0) / 100.0
  const diff = game.k_factor * (score - we)
  const rounded = Math.round(diff)
  return rounded >= 0 ? `+${rounded}` : `${rounded}`
}

// SVG ELO Chart coordinates
const chartWidth = 800
const chartHeight = 180
const paddingLeft = 50
const paddingRight = 20
const paddingTop = 30
const paddingBottom = 40

const chartMinMax = computed(() => {
  if (!ratings.value || ratings.value.length === 0) {
    return { min: 1000, max: 2000 }
  }
  const elos = ratings.value.map(r => r.rating)
  let min = Math.min(...elos)
  let max = Math.max(...elos)
  
  // Pad the range slightly
  min = Math.max(0, min - 50)
  max = max + 50
  
  // Prevent division by zero
  if (min === max) {
    min -= 50
    max += 50
  }
  return { min, max }
})

const chartPoints = computed(() => {
  if (!ratings.value || ratings.value.length === 0) return []
  
  const { min, max } = chartMinMax.value
  const total = ratings.value.length
  
  return ratings.value.map((r, index) => {
    // X distribution
    const x = total > 1 
      ? paddingLeft + index * (chartWidth - paddingLeft - paddingRight) / (total - 1)
      : paddingLeft + (chartWidth - paddingLeft - paddingRight) / 2
      
    // Y distribution
    const y = (chartHeight - paddingBottom) - 
      (r.rating - min) * (chartHeight - paddingBottom - paddingTop) / (max - min)
      
    return {
      x,
      y,
      period: r.period,
      rating: r.rating
    }
  })
})

const chartPath = computed(() => {
  const pts = chartPoints.value
  if (pts.length === 0) return ""
  return pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(" ")
})

// Grid lines helper
const yGridLines = computed(() => {
  const { min, max } = chartMinMax.value
  const lines = []
  
  // Determine step size (e.g. 100 points)
  const step = 100
  const start = Math.ceil(min / step) * step
  
  for (let val = start; val < max; val += step) {
    const y = (chartHeight - paddingBottom) - 
      (val - min) * (chartHeight - paddingBottom - paddingTop) / (max - min)
    lines.push({ y, value: val })
  }
  return lines
})

const xGridLines = computed(() => {
  const pts = chartPoints.value
  if (pts.length <= 1) return []
  
  const lines = []
  // Only label every Nth point to avoid overlap
  const total = pts.length
  let step = 1
  if (total > 20) step = 4
  else if (total > 10) step = 2
  
  for (let i = 0; i < total; i += step) {
    lines.push(pts[i])
  }
  // Make sure last one is labeled
  if ((total - 1) % step !== 0) {
    lines.push(pts[total - 1])
  }
  return lines
})

function formatPeriod(periodStr) {
  if (!periodStr || periodStr.length !== 6) return periodStr
  const year = periodStr.substring(0, 4)
  const month = periodStr.substring(4, 6)
  
  const months = {
    "01": "Jan", "04": "Apr", "07": "Jul", "10": "Oct"
  }
  return `${months[month] || month} ${year}`
}

function cleanTournament(tourney) {
  if (!tourney) return ""
  let name = tourney.replace(/\.\d+$/, "")
  name = name.replace(/^(S_SWAR_[^_]+_|S_SWAR_|S_)/i, "")
  return name.replace(/_/g, " ").trim()
}

onMounted(() => {
  let l = route.query.locale
  locale.value = ["en", "nl", "fr", "de"].includes(l) ? l : "nl"

  // Send message to parent iframe if embedded
  if (typeof window !== "undefined" && window.parent !== window) {
    const resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        window.parent.postMessage({
          type: "kbsb-iframe-resize",
          height: entry.target.scrollHeight
        }, "*")
      }
    })
    resizeObserver.observe(document.body)
    onUnmounted(() => {
      resizeObserver.disconnect()
    })
  }
})
</script>

<template>
  <v-container class="my-4">
    <!-- Header -->
    <v-row class="mb-4 align-center">
      <v-col cols="auto">
        <h1 class="text-h4 font-weight-bold text-green-darken-3">
          {{ t('arc.title') }}
        </h1>
      </v-col>
    </v-row>

    <!-- Error notice -->
    <v-alert v-if="errorText" type="error" closable class="mb-4" @click:close="errorText = ''">
      {{ errorText }}
    </v-alert>

    <!-- VIEW 1: SEARCH PLAYER / CLUB -->
    <div v-if="!selectedPlayer">
      <!-- IF A CLUB IS SELECTED -->
      <div v-if="selectedClub">
        <v-btn 
          color="green-darken-2" 
          variant="outlined" 
          prepend-icon="mdi-arrow-left" 
          class="mb-4"
          @click="selectedClub = null"
        >
          {{ t('arc.back_to_clubs') || 'Terug naar clubs' }}
        </v-btn>

        <v-card class="mb-6 border-green bg-green-lighten-5">
          <v-card-text class="d-flex align-center justify-space-between py-4">
            <div>
              <div class="text-subtitle-2 text-grey-darken-1">{{ t('arc.selected_club') || 'Geselecteerde Club' }}</div>
              <div class="text-h5 font-weight-bold text-green-darken-4">
                {{ selectedClub.name }} ({{ selectedClub.club_id }})
              </div>
            </div>
            <v-chip color="green-darken-3" class="font-weight-bold" variant="flat">
              {{ clubPlayers.length }} {{ t('arc.players_count') || 'spelers' }}
            </v-chip>
          </v-card-text>
        </v-card>

        <v-row v-if="loadingClubPlayers" justify="center" class="my-8">
          <v-progress-circular indeterminate color="green" size="64"></v-progress-circular>
        </v-row>

        <!-- Club players table (sorted by latest ELO) -->
        <v-card v-else class="elevation-2">
          <v-card-text class="pa-0">
            <v-table hover>
              <thead class="bg-green-lighten-5">
                <tr>
                  <th @click="toggleSortClub('name')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                    {{ t('arc.player_name') }}
                    <v-icon size="small" class="ml-1">
                      {{ clubSortKey === 'name' ? (clubSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                    </v-icon>
                  </th>
                  <th @click="toggleSortClub('member_id')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                    {{ t('arc.member_id') }}
                    <v-icon size="small" class="ml-1">
                      {{ clubSortKey === 'member_id' ? (clubSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                    </v-icon>
                  </th>
                  <th @click="toggleSortClub('latest_elo')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                    {{ t('arc.last_elo') || 'Laatste ELO' }}
                    <v-icon size="small" class="ml-1">
                      {{ clubSortKey === 'latest_elo' ? (clubSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                    </v-icon>
                  </th>
                  <th @click="toggleSortClub('gender')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                    {{ t('arc.gender') }}
                    <v-icon size="small" class="ml-1">
                      {{ clubSortKey === 'gender' ? (clubSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                    </v-icon>
                  </th>
                  <th @click="toggleSortClub('birthdate')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                    {{ t('arc.birthyear') }}
                    <v-icon size="small" class="ml-1">
                      {{ clubSortKey === 'birthdate' ? (clubSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                    </v-icon>
                  </th>
                  <th @click="toggleSortClub('nationality')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                    {{ t('arc.nationality') }}
                    <v-icon size="small" class="ml-1">
                      {{ clubSortKey === 'nationality' ? (clubSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                    </v-icon>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="p in sortedClubPlayers" 
                  :key="p.member_id" 
                  @click="selectPlayer(p.member_id)" 
                  style="cursor: pointer;"
                >
                  <td class="text-green-darken-3 font-weight-medium">{{ p.name }}</td>
                  <td>{{ p.member_id }}</td>
                  <td class="font-weight-bold text-green-darken-2">{{ p.latest_elo || 'N/A' }}</td>
                  <td>{{ p.gender }}</td>
                  <td>{{ p.birthdate ? p.birthdate.substring(0, 4) : 'N/A' }}</td>
                  <td>{{ p.nationality || 'BEL' }}</td>
                </tr>
              </tbody>
            </v-table>
          </v-card-text>
        </v-card>
      </div>

      <!-- ELSE (NO CLUB SELECTED) -->
      <div v-else>
        <!-- Tabs to select search mode -->
        <v-tabs v-slot:default v-model="searchMode" color="green-darken-3" class="mb-6 bg-green-lighten-5 rounded elevation-1">
          <v-tab value="player" prepend-icon="mdi-account-search">
            {{ t('arc.search_player_tab') || 'Speler' }}
          </v-tab>
          <v-tab value="club" prepend-icon="mdi-home-group">
            {{ t('arc.search_club_tab') || 'Club' }}
          </v-tab>
          <v-tab value="region" prepend-icon="mdi-map-marker-multiple">
            {{ t('arc.regions_tab') || 'Regio\'s' }}
          </v-tab>
        </v-tabs>

        <!-- MODE 1: PLAYER SEARCH -->
        <div v-if="searchMode === 'player'">
          <v-card class="mb-6 elevation-2 border-green">
            <v-card-text>
              <v-form @submit.prevent="handleSearch">
                <v-row align="center">
                  <v-col cols="12" md="9">
                    <v-text-field
                      v-model="searchQuery"
                      prepend-inner-icon="mdi-magnify"
                      :label="t('arc.search_placeholder')"
                      variant="outlined"
                      color="green-darken-2"
                      hide-details
                      required
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="3">
                    <v-btn
                      block
                      size="large"
                      color="green-darken-2"
                      type="submit"
                      :loading="searching"
                      prepend-icon="mdi-search-web"
                    >
                      {{ t('arc.search_btn') }}
                    </v-btn>
                  </v-col>
                </v-row>
              </v-form>
            </v-card-text>
          </v-card>

          <!-- Player search results list -->
          <v-card v-if="hasSearched && !searching" class="elevation-2">
            <v-card-text v-if="players.length === 0" class="text-center py-8 text-muted">
              <v-icon size="48" color="grey-lighten-1" class="mb-2">mdi-account-search-outline</v-icon>
              <p class="text-subtitle-1">{{ t('arc.no_results') }}</p>
            </v-card-text>
            <v-card-text v-else class="pa-0">
              <v-table hover>
                <thead class="bg-green-lighten-5">
                  <tr>
                    <th @click="toggleSortSearch('name')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                      {{ t('arc.player_name') }}
                      <v-icon size="small" class="ml-1">
                        {{ searchSortKey === 'name' ? (searchSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                      </v-icon>
                    </th>
                    <th @click="toggleSortSearch('member_id')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                      {{ t('arc.member_id') }}
                      <v-icon size="small" class="ml-1">
                        {{ searchSortKey === 'member_id' ? (searchSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                      </v-icon>
                    </th>
                    <th @click="toggleSortSearch('fide_id')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                      FIDE ID
                      <v-icon size="small" class="ml-1">
                        {{ searchSortKey === 'fide_id' ? (searchSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                      </v-icon>
                    </th>
                    <th @click="toggleSortSearch('latest_elo')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                      {{ t('arc.last_elo') || 'Laatste ELO' }}
                      <v-icon size="small" class="ml-1">
                        {{ searchSortKey === 'latest_elo' ? (searchSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                      </v-icon>
                    </th>
                    <th @click="toggleSortSearch('gender')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                      {{ t('arc.gender') }}
                      <v-icon size="small" class="ml-1">
                        {{ searchSortKey === 'gender' ? (searchSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                      </v-icon>
                    </th>
                    <th @click="toggleSortSearch('birthdate')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                      {{ t('arc.birthyear') }}
                      <v-icon size="small" class="ml-1">
                        {{ searchSortKey === 'birthdate' ? (searchSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                      </v-icon>
                    </th>
                    <th @click="toggleSortSearch('nationality')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                      {{ t('arc.nationality') }}
                      <v-icon size="small" class="ml-1">
                        {{ searchSortKey === 'nationality' ? (searchSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                      </v-icon>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr 
                    v-for="p in sortedPlayers" 
                    :key="p.member_id" 
                    @click="selectPlayer(p.member_id)" 
                    style="cursor: pointer;"
                  >
                    <td class="text-green-darken-3 font-weight-medium">{{ p.name }}</td>
                    <td>{{ p.member_id }}</td>
                    <td>{{ p.fide_id || 'N/A' }}</td>
                    <td class="font-weight-bold text-green-darken-2">{{ p.latest_elo || 'N/A' }}</td>
                    <td>{{ p.gender }}</td>
                    <td>{{ p.birthdate ? p.birthdate.substring(0, 4) : 'N/A' }}</td>
                    <td>{{ p.nationality || 'BEL' }}</td>
                  </tr>
                </tbody>
              </v-table>
            </v-card-text>
          </v-card>

          <v-row v-if="searching" justify="center" class="my-8">
            <v-progress-circular indeterminate color="green" size="64"></v-progress-circular>
          </v-row>
        </div>

        <!-- MODE 2: CLUB SEARCH -->
        <div v-else-if="searchMode === 'club'">
          <v-card class="mb-6 elevation-2 border-green">
            <v-card-text>
              <v-form @submit.prevent="handleClubSearch">
                <v-row align="center">
                  <v-col cols="12" md="9">
                    <v-text-field
                      v-model="clubSearchQuery"
                      prepend-inner-icon="mdi-home-search"
                      :label="t('arc.search_club_placeholder') || 'Zoek clubnaam of clubnummer...'"
                      variant="outlined"
                      color="green-darken-2"
                      hide-details
                      required
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="3">
                    <v-btn
                      block
                      size="large"
                      color="green-darken-2"
                      type="submit"
                      :loading="searchingClubs"
                      prepend-icon="mdi-magnify"
                    >
                      {{ t('arc.search_btn') }}
                    </v-btn>
                  </v-col>
                </v-row>
              </v-form>
            </v-card-text>
          </v-card>

          <!-- Club list search results -->
          <v-card v-if="hasSearchedClubs && !searchingClubs" class="elevation-2">
            <v-card-text v-if="clubs.length === 0" class="text-center py-8 text-muted">
              <v-icon size="48" color="grey-lighten-1" class="mb-2">mdi-home-alert-outline</v-icon>
              <p class="text-subtitle-1">{{ t('arc.no_clubs') || 'Geen clubs gevonden.' }}</p>
            </v-card-text>
            <v-card-text v-else class="pa-0">
              <v-table hover>
                <thead class="bg-green-lighten-5">
                  <tr>
                    <th class="font-weight-bold">{{ t('arc.club_id') || 'Clubnummer' }}</th>
                    <th class="font-weight-bold">{{ t('arc.club_name') || 'Clubnaam' }}</th>
                    <th class="font-weight-bold">{{ t('arc.club_players_count') || 'Ledental' }}</th>
                    <th class="font-weight-bold">Fed</th>
                  </tr>
                </thead>
                <tbody>
                  <tr 
                    v-for="c in clubs" 
                    :key="c.club_id" 
                    @click="selectClub(c)" 
                    style="cursor: pointer;"
                  >
                    <td class="font-weight-bold text-green-darken-3">{{ c.club_id }}</td>
                    <td class="font-weight-medium">{{ c.name }}</td>
                    <td>{{ c.player_count || 0 }}</td>
                    <td><v-chip size="small" variant="outlined" color="green">{{ c.federation }}</v-chip></td>
                  </tr>
                </tbody>
              </v-table>
            </v-card-text>
          </v-card>

          <v-row v-if="searchingClubs" justify="center" class="my-8">
            <v-progress-circular indeterminate color="green" size="64"></v-progress-circular>
          </v-row>
        </div>

        <!-- MODE 3: REGIONS -->
        <div v-else-if="searchMode === 'region'">
          <v-row v-if="loadingRegions" justify="center" class="my-8">
            <v-progress-circular indeterminate color="green" size="64"></v-progress-circular>
          </v-row>
          
          <div v-else>
            <div v-for="region in regionsList" :key="region.id">
              <div v-if="regionsClubs[region.id] && regionsClubs[region.id].length > 0" class="mb-8">
                <h2 class="text-h5 font-weight-bold text-green-darken-3 mb-4 pb-2" style="border-bottom: 2px solid #e0e0e0;">
                  {{ region.name }}
                </h2>
                
                <v-card class="elevation-1 pa-4 bg-grey-lighten-4">
                  <v-row>
                    <v-col 
                      v-for="club in regionsClubs[region.id]" 
                      :key="club.club_id"
                      cols="12"
                      sm="6"
                      md="4"
                      lg="3"
                    >
                      <v-card 
                        variant="outlined" 
                        color="green-darken-1" 
                        class="h-100 hover-card bg-white" 
                        @click="selectClub(club)"
                        style="cursor: pointer;"
                      >
                        <v-card-text class="d-flex align-center justify-space-between py-3 px-4">
                          <div class="text-truncate">
                            <div class="text-caption text-grey-darken-1 font-weight-bold">{{ club.club_id }}</div>
                            <div class="font-weight-bold text-green-darken-4 text-truncate">
                              {{ club.name }}
                            </div>
                          </div>
                          <v-chip size="x-small" color="green-darken-3" class="font-weight-bold ml-2">
                            {{ club.player_count }}
                          </v-chip>
                        </v-card-text>
                      </v-card>
                    </v-col>
                  </v-row>
                </v-card>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- VIEW 2: PLAYER PROFILE & HISTORY -->
    <div v-else>
      <v-btn 
        color="green-darken-2" 
        variant="outlined" 
        prepend-icon="mdi-arrow-left" 
        class="mb-6"
        @click="selectedPlayer = null"
      >
        {{ t('arc.back_to_search') }}
      </v-btn>

      <v-row v-if="profileLoading" justify="center" class="my-12">
        <v-progress-circular indeterminate color="green" size="64"></v-progress-circular>
      </v-row>

      <div v-else>
        <!-- Player details box -->
        <v-card class="mb-6 border-green bg-green-lighten-5">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <div class="text-subtitle-2 text-grey-darken-1">{{ t('arc.player_name') }}</div>
                <div class="text-h5 font-weight-bold text-green-darken-4">{{ selectedPlayer.name }}</div>
                <div class="text-subtitle-2 text-grey-darken-2" v-if="selectedPlayer.club_id">
                  Club: 
                  <span 
                    @click="goToClub({ club_id: selectedPlayer.club_id, name: selectedPlayer.club_name })" 
                    class="text-green-darken-3 font-weight-medium text-decoration-underline" 
                    style="cursor: pointer;"
                  >
                    {{ selectedPlayer.club_name || selectedPlayer.club_id }} ({{ selectedPlayer.club_id }})
                  </span>
                </div>
              </v-col>
              <v-col cols="6" sm="3" md="1.5">
                <div class="text-subtitle-2 text-grey-darken-1">{{ t('arc.member_id') }}</div>
                <div class="text-h6 font-weight-bold">{{ selectedPlayer.member_id }}</div>
              </v-col>
              <v-col cols="6" sm="3" md="1.5">
                <div class="text-subtitle-2 text-grey-darken-1">FIDE-ID</div>
                <div class="text-h6 font-weight-bold">
                  <a v-if="selectedPlayer.fide_id" :href="`https://ratings.fide.com/profile/${selectedPlayer.fide_id}`" target="_blank" class="text-green-darken-2 text-decoration-none">
                    {{ selectedPlayer.fide_id }}
                    <v-icon size="x-small" class="ml-1">mdi-open-in-new</v-icon>
                  </a>
                  <span v-else>N/A</span>
                </div>
              </v-col>
              <v-col cols="6" sm="3" md="0.5" class="px-1">
                <div class="text-subtitle-2 text-grey-darken-1">{{ t('arc.gender') }}</div>
                <div class="text-h6">{{ selectedPlayer.gender }}</div>
              </v-col>
              <v-col cols="6" sm="3" md="1">
                <div class="text-subtitle-2 text-grey-darken-1">{{ t('arc.birthyear') }}</div>
                <div class="text-h6">{{ selectedPlayer.birthdate ? selectedPlayer.birthdate.substring(0, 4) : 'N/A' }}</div>
              </v-col>
              <v-col cols="6" sm="3" md="1">
                <div class="text-subtitle-2 text-grey-darken-1">{{ t('arc.nationality') }}</div>
                <div class="text-h6">{{ selectedPlayer.nationality || 'BEL' }}</div>
              </v-col>
              <v-col cols="6" sm="3" md="1.5">
                <div class="text-subtitle-2 text-grey-darken-1">{{ t('arc.total_games') || 'Aantal partijen' }}</div>
                <div class="text-h6 font-weight-bold text-green-darken-3">{{ totalGames || 0 }}</div>
              </v-col>
              <v-col cols="6" sm="3" md="2">
                <div class="text-subtitle-2 text-grey-darken-1">{{ t('arc.latest_game') || 'Laatste partij' }}</div>
                <div class="text-h6 font-weight-bold text-green-darken-3">{{ latestGameDate || 'N/A' }}</div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- ELO rating evolution chart -->
        <v-card class="mb-6 elevation-2">
          <v-card-title class="d-flex align-center justify-space-between pt-4 px-6" style="min-height: 56px;">
            <span class="text-h6 font-weight-bold text-green-darken-3">{{ t('arc.elo_evolution') }}</span>
            <span class="text-subtitle-1 bg-green-lighten-4 px-3 py-1 rounded text-green-darken-4 font-weight-bold" :style="{ visibility: hoveredPoint ? 'visible' : 'hidden' }">
              {{ hoveredPoint ? `${formatPeriod(hoveredPoint.period)}: ${hoveredPoint.rating} ELO` : '&nbsp;' }}
            </span>
          </v-card-title>
          
          <v-card-text class="py-4">
            <div class="chart-container" style="position: relative; width: 100%; overflow-x: auto;">
              <svg 
                :viewBox="`0 0 ${chartWidth} ${chartHeight}`" 
                width="100%" 
                style="min-width: 600px; height: auto; display: block;"
              >
                <!-- Background grid lines (Y-axis) -->
                <line 
                  v-for="line in yGridLines" 
                  :key="line.value"
                  :x1="paddingLeft" 
                  :y1="line.y" 
                  :x2="chartWidth - paddingRight" 
                  :y2="line.y"
                  stroke="#e2e8f0" 
                  stroke-dasharray="4,4" 
                  stroke-width="1"
                />
                
                <!-- Y-axis labels -->
                <text 
                  v-for="line in yGridLines" 
                  :key="'lbl-' + line.value"
                  :x="paddingLeft - 8" 
                  :y="line.y + 4" 
                  text-anchor="end" 
                  fill="#64748b" 
                  font-size="11"
                  font-weight="500"
                >
                  {{ line.value }}
                </text>

                <!-- X-axis grid lines & labels -->
                <g v-for="pt in xGridLines" :key="pt.period">
                  <line 
                    :x1="pt.x" 
                    :y1="paddingTop" 
                    :x2="pt.x" 
                    :y2="chartHeight - paddingBottom" 
                    stroke="#e2e8f0" 
                    stroke-width="1"
                  />
                  <text 
                    :x="pt.x" 
                    :y="chartHeight - paddingBottom + 18" 
                    text-anchor="middle" 
                    fill="#64748b" 
                    font-size="10"
                    font-weight="500"
                    :transform="'rotate(-25, ' + pt.x + ', ' + (chartHeight - paddingBottom + 18) + ')'"
                  >
                    {{ formatPeriod(pt.period) }}
                  </text>
                </g>

                <!-- SVG rating path line -->
                <path 
                  :d="chartPath" 
                  fill="none" 
                  stroke="#16a34a" 
                  stroke-width="3.5" 
                  stroke-linejoin="round"
                  stroke-linecap="round"
                />

                <!-- SVG rating data points -->
                <circle 
                  v-for="pt in chartPoints" 
                  :key="pt.period"
                  :cx="pt.x" 
                  :cy="pt.y" 
                  r="5" 
                  :fill="filteredPeriod === pt.period ? '#dc2626' : '#ffffff'" 
                  :stroke="filteredPeriod === pt.period ? '#dc2626' : '#16a34a'" 
                  stroke-width="3"
                  style="cursor: pointer; transition: r 0.15s;"
                  @mouseover="hoveredPoint = pt"
                  @mouseleave="hoveredPoint = null"
                  @click="filteredPeriod = filteredPeriod === pt.period ? 'All' : pt.period"
                />
              </svg>
            </div>
          </v-card-text>
        </v-card>

        <!-- Game History list -->
        <v-card class="elevation-2">
          <v-card-title class="d-flex align-center justify-space-between pt-4 px-6 pb-2">
            <span class="text-h6 font-weight-bold text-green-darken-3">
              {{ t('arc.game_history') }}
              <v-chip 
                v-if="filteredPeriod !== 'All'" 
                closable 
                size="small" 
                color="green" 
                class="ml-2 font-weight-bold"
                @click:close="filteredPeriod = 'All'"
              >
                {{ formatPeriod(filteredPeriod) }}
              </v-chip>
            </span>
            <v-select
              v-model="filteredPeriod"
              :items="periodsList"
              hide-details
              density="compact"
              variant="outlined"
              color="green"
              style="max-width: 180px;"
            >
              <template v-slot:item="{ props, item }">
                <v-list-item v-bind="props" :title="item.value === 'All' ? 'All Periods' : formatPeriod(item.value)"></v-list-item>
              </template>
              <template v-slot:selection="{ item }">
                <span>{{ item.value === "All" ? "All Periods" : formatPeriod(item.value) }}</span>
              </template>
            </v-select>
          </v-card-title>
          
          <v-card-text class="pa-0">
            <v-table hover>
              <thead class="bg-green-lighten-5">
                <tr>
                  <th @click="toggleSortGames('period')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                    {{ t('arc.period') }}
                    <v-icon size="small" class="ml-1">
                      {{ gamesSortKey === 'period' ? (gamesSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                    </v-icon>
                  </th>
                  <th @click="toggleSortGames('date')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                    {{ t('arc.date') }}
                    <v-icon size="small" class="ml-1">
                      {{ gamesSortKey === 'date' ? (gamesSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                    </v-icon>
                  </th>
                  <th @click="toggleSortGames('game_number')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                    {{ t('arc.game_nr') || 'Partijnr.' }}
                    <v-icon size="small" class="ml-1">
                      {{ gamesSortKey === 'game_number' ? (gamesSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                    </v-icon>
                  </th>
                  <th @click="toggleSortGames('tournament')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                    {{ t('arc.tournament') }}
                    <v-icon size="small" class="ml-1">
                      {{ gamesSortKey === 'tournament' ? (gamesSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                    </v-icon>
                  </th>
                  <th @click="toggleSortGames('opponent_name')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                    {{ t('arc.opponent') }}
                    <v-icon size="small" class="ml-1">
                      {{ gamesSortKey === 'opponent_name' ? (gamesSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                    </v-icon>
                  </th>
                  <th @click="toggleSortGames('opponent_elo')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                    {{ t('arc.rating') }}
                    <v-icon size="small" class="ml-1">
                      {{ gamesSortKey === 'opponent_elo' ? (gamesSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                    </v-icon>
                  </th>
                  <th @click="toggleSortGames('color')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                    {{ t('arc.color') }}
                    <v-icon size="small" class="ml-1">
                      {{ gamesSortKey === 'color' ? (gamesSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                    </v-icon>
                  </th>
                  <th @click="toggleSortGames('k_factor')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                    K
                    <v-icon size="small" class="ml-1">
                      {{ gamesSortKey === 'k_factor' ? (gamesSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                    </v-icon>
                  </th>
                  <th @click="toggleSortGames('expected_score')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                    +/-
                    <v-icon size="small" class="ml-1">
                      {{ gamesSortKey === 'expected_score' ? (gamesSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                    </v-icon>
                  </th>
                  <th @click="toggleSortGames('result')" class="font-weight-bold" style="cursor: pointer; user-select: none;">
                    {{ t('arc.result') }}
                    <v-icon size="small" class="ml-1">
                      {{ gamesSortKey === 'result' ? (gamesSortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
                    </v-icon>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="g in sortedGames" :key="g.id">
                  <td>{{ formatPeriod(g.period) }}</td>
                  <td>{{ g.date || 'N/A' }}</td>
                  <td>{{ g.game_number || '-' }}</td>
                  <td class="text-truncate" style="max-width: 180px;" :title="g.tournament">{{ cleanTournament(g.tournament) }}</td>
                  <td class="font-weight-medium">
                    <span 
                      v-if="g.opponent_member_id && g.opponent_member_id > 0"
                      @click="selectPlayer(g.opponent_member_id)" 
                      class="text-green-darken-3 font-weight-medium text-decoration-underline" 
                      style="cursor: pointer;"
                    >
                      {{ g.opponent_name }}
                    </span>
                    <span v-else>{{ g.opponent_name }}</span>
                  </td>
                  <td>{{ g.opponent_elo !== null ? g.opponent_elo : 'N/A' }}</td>
                  <td>
                    <v-icon :color="g.color === 'W' ? 'grey-darken-3' : 'grey-lighten-1'">
                      {{ g.color === 'W' ? 'mdi-checkbox-blank' : 'mdi-checkbox-blank-outline' }}
                    </v-icon>
                    <span class="ml-1">{{ g.color === 'W' ? t('arc.white') : t('arc.black') }}</span>
                  </td>
                  <td>{{ g.k_factor || '-' }}</td>
                  <td>
                    <span :class="getEloChange(g).startsWith('+') ? 'text-green-darken-2 font-weight-bold' : (getEloChange(g).startsWith('-') ? 'text-red-darken-2 font-weight-bold' : '')">
                      {{ getEloChange(g) }}
                    </span>
                  </td>
                  <td>
                    <v-chip
                      :color="getPlayerResultColor(g)"
                      size="small"
                      variant="flat"
                      text-color="white"
                      class="font-weight-bold"
                      style="min-width: 28px; justify-content: center;"
                    >
                      {{ getPlayerResultText(g) }}
                    </v-chip>
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-card-text>
        </v-card>
      </div>
    </div>
  </v-container>
</template>

<style scoped>
.border-green {
  border-left: 5px solid #1b5e20 !important;
}
.chart-container svg text {
  user-select: none;
}
.hover-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}
.hover-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(27, 94, 32, 0.15) !important;
  background-color: #f1f8e9 !important; /* green-lighten-5 */
}
</style>

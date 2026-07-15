<script setup>
import { ref, computed, onMounted } from "vue"
import { useRoute } from "vue-router"
import { useI18n } from "vue-i18n"

const { t, locale } = useI18n()
const route = useRoute()
const { $backend } = useNuxtApp()

definePageMeta({
  layout: "nomenu",
})

// Search Mode ('player' or 'club')
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

// Hovered chart point state
const hoveredPoint = ref(null)

// API methods
async function handleSearch() {
  if (!searchQuery.value || searchQuery.value.trim().length < 2) return
  searching.value = true
  hasSearched.value = true
  errorText.value = ""
  players.value = []
  
  try {
    const res = await $backend("archive", "search", { q: searchQuery.value })
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
    const res = await $backend("archive", "searchClubs", { q: clubSearchQuery.value })
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
    const res = await $backend("archive", "getClubPlayers", { club_id: club.club_id })
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
  
  try {
    const res = await $backend("archive", "getProfile", { member_id: memberId })
    if (res && res.data && res.data.success) {
      selectedPlayer.value = res.data.player
      ratings.value = res.data.ratings
      games.value = res.data.games
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
      <!-- Tabs to select search mode -->
      <v-tabs v-slot:default v-model="searchMode" color="green-darken-3" class="mb-6 bg-green-lighten-5 rounded elevation-1">
        <v-tab value="player" prepend-icon="mdi-account-search">
          {{ t('arc.search_player_tab') || 'Speler' }}
        </v-tab>
        <v-tab value="club" prepend-icon="mdi-home-group">
          {{ t('arc.search_club_tab') || 'Club' }}
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
                  <th class="font-weight-bold">{{ t('arc.player_name') }}</th>
                  <th class="font-weight-bold">{{ t('arc.member_id') }}</th>
                  <th class="font-weight-bold">{{ t('arc.last_elo') || 'Laatste ELO' }}</th>
                  <th class="font-weight-bold">{{ t('arc.gender') }}</th>
                  <th class="font-weight-bold">{{ t('arc.birthyear') }}</th>
                  <th class="font-weight-bold">{{ t('arc.nationality') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="p in players" 
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

        <v-row v-if="searching" justify="center" class="my-8">
          <v-progress-circular indeterminate color="green" size="64"></v-progress-circular>
        </v-row>
      </div>

      <!-- MODE 2: CLUB SEARCH -->
      <div v-else>
        <!-- Club search form if no club selected -->
        <div v-if="!selectedClub">
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
                    <th class="font-weight-bold">{{ t('arc.abbrev') || 'Afkorting' }}</th>
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
                    <td>{{ c.abbreviation || '-' }}</td>
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

        <!-- Selected Club: Display Players sorted by Latest ELO -->
        <div v-else>
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
                    <th class="font-weight-bold">{{ t('arc.player_name') }}</th>
                    <th class="font-weight-bold">{{ t('arc.member_id') }}</th>
                    <th class="font-weight-bold">{{ t('arc.last_elo') || 'Laatste ELO' }}</th>
                    <th class="font-weight-bold">{{ t('arc.gender') }}</th>
                    <th class="font-weight-bold">{{ t('arc.birthyear') }}</th>
                    <th class="font-weight-bold">{{ t('arc.nationality') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr 
                    v-for="p in clubPlayers" 
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
              <v-col cols="12" md="4">
                <div class="text-subtitle-2 text-grey-darken-1">{{ t('arc.player_name') }}</div>
                <div class="text-h5 font-weight-bold text-green-darken-4">{{ selectedPlayer.name }}</div>
              </v-col>
              <v-col cols="6" sm="3" md="2">
                <div class="text-subtitle-2 text-grey-darken-1">{{ t('arc.member_id') }}</div>
                <div class="text-h6 font-weight-bold">{{ selectedPlayer.member_id }}</div>
              </v-col>
              <v-col cols="6" sm="3" md="2">
                <div class="text-subtitle-2 text-grey-darken-1">{{ t('arc.gender') }}</div>
                <div class="text-h6">{{ selectedPlayer.gender }}</div>
              </v-col>
              <v-col cols="6" sm="3" md="2">
                <div class="text-subtitle-2 text-grey-darken-1">{{ t('arc.birthyear') }}</div>
                <div class="text-h6">{{ selectedPlayer.birthdate ? selectedPlayer.birthdate.substring(0, 4) : 'N/A' }}</div>
              </v-col>
              <v-col cols="6" sm="3" md="2">
                <div class="text-subtitle-2 text-grey-darken-1">{{ t('arc.nationality') }}</div>
                <div class="text-h6">{{ selectedPlayer.nationality || 'BEL' }}</div>
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
                  fill="#ffffff" 
                  stroke="#16a34a" 
                  stroke-width="3"
                  style="cursor: pointer; transition: r 0.15s;"
                  @mouseover="hoveredPoint = pt"
                  @mouseleave="hoveredPoint = null"
                />
              </svg>
            </div>
          </v-card-text>
        </v-card>

        <!-- Game History list -->
        <v-card class="elevation-2">
          <v-card-title class="d-flex align-center justify-space-between pt-4 px-6 pb-2">
            <span class="text-h6 font-weight-bold text-green-darken-3">{{ t('arc.game_history') }}</span>
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
                  <th class="font-weight-bold">{{ t('arc.period') }}</th>
                  <th class="font-weight-bold">{{ t('arc.date') }}</th>
                  <th class="font-weight-bold">{{ t('arc.tournament') }}</th>
                  <th class="font-weight-bold">{{ t('arc.opponent') }}</th>
                  <th class="font-weight-bold">{{ t('arc.rating') }}</th>
                  <th class="font-weight-bold">{{ t('arc.color') }}</th>
                  <th class="font-weight-bold">{{ t('arc.result') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="g in filteredGames" :key="g.id">
                  <td>{{ formatPeriod(g.period) }}</td>
                  <td>{{ g.date || 'N/A' }}</td>
                  <td class="text-truncate" style="max-width: 250px;" :title="g.tournament">{{ cleanTournament(g.tournament) }}</td>
                  <td class="font-weight-medium">{{ g.opponent_name }}</td>
                  <td>{{ g.opponent_elo || 'N/A' }}</td>
                  <td>
                    <v-icon :color="g.color === 'W' ? 'grey-darken-3' : 'grey-lighten-1'">
                      {{ g.color === 'W' ? 'mdi-checkbox-blank' : 'mdi-checkbox-blank-outline' }}
                    </v-icon>
                    <span class="ml-1">{{ g.color === 'W' ? 'White' : 'Black' }}</span>
                  </td>
                  <td>
                    <v-chip
                      :color="g.result === '1-0' ? 'green-darken-1' : (g.result === '1/2' ? 'grey-darken-1' : 'red-darken-1')"
                      size="small"
                      variant="flat"
                      text-color="white"
                      class="font-weight-bold"
                    >
                      {{ g.result }}
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
</style>

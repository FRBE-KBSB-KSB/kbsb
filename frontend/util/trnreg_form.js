// The tournament registration form's own logic, kept here so it can be tested
// without a browser (tests/trnreg_form.test.mjs). From Luc's remarks of
// 26 Nov 2026, his first try of a team tournament.

function isoDay(v) {
  const m = String(v || "").match(/^(\d{4})-(\d{2})-(\d{2})/)
  return m ? `${m[1]}-${m[2]}-${m[3]}` : ""
}

function addDays(iso, n) {
  const [y, m, d] = iso.split("-").map(Number)
  return new Date(Date.UTC(y, m - 1, d + n)).toISOString().slice(0, 10)
}

function daysBetween(a, b) {
  const [y1, m1, d1] = a.split("-").map(Number)
  const [y2, m2, d2] = b.split("-").map(Number)
  return Math.round((Date.UTC(y2, m2 - 1, d2) - Date.UTC(y1, m1 - 1, d1)) / 86400000)
}

// One day: the same start and end, or no end date (the API reads a missing
// end as the start day too). Every round is on that day.
export function isSingleDay(start, end) {
  const s = isoDay(start)
  if (!s) return false
  const e = isoDay(end)
  return !e || e === s
}

// A date for each of `n` rounds from the start, never past the end: one a
// day while there are days enough, otherwise several a day, in order, the
// first days taking the extra rounds. "One per day" on a tournament of
// 18/12 to 18/12 filled 15 days up to 1 January (Luc, 26 Nov 2026).
export function spreadRoundDates(start, end, n) {
  const s = isoDay(start)
  if (!s || !(n > 0)) return []
  let e = isoDay(end) || s
  if (e < s) e = s
  const days = daysBetween(s, e) + 1
  return Array.from({ length: n }, (_, i) => addDays(s, days >= n ? i : Math.floor((i * days) / n)))
}

function validDay(y, m, d) {
  if (y < 1900 || y > 2100 || m < 1 || m > 12 || d < 1) return false
  return d <= new Date(Date.UTC(y, m, 0)).getUTCDate()
}

function pad(n) {
  return String(n).padStart(2, "0")
}

// What is typed in the birth date box, as YYYY-MM-DD: a day (31/12/2009,
// 31-12-2009, 31.12.2009 or 2009-12-31) or a year alone, which is 1 January
// of it. "" for nothing typed, null for something that is no date.
export function parseBirthInput(text) {
  const s = String(text ?? "").trim()
  if (!s) return ""
  let m = s.match(/^(\d{4})$/)
  if (m) return validDay(Number(m[1]), 1, 1) ? `${m[1]}-01-01` : null
  m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/)
  if (m) {
    const [y, mo, d] = [Number(m[1]), Number(m[2]), Number(m[3])]
    return validDay(y, mo, d) ? `${y}-${pad(mo)}-${pad(d)}` : null
  }
  m = s.match(/^(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})$/)
  if (m) {
    const [d, mo, y] = [Number(m[1]), Number(m[2]), Number(m[3])]
    return validDay(y, mo, d) ? `${y}-${pad(mo)}-${pad(d)}` : null
  }
  return null
}

// A stored date as the box shows it: 31/12/2009.
export function formatBirthInput(iso) {
  const d = isoDay(iso)
  if (!d) return ""
  const [y, m, day] = d.split("-")
  return `${day}/${m}/${y}`
}

// The birth year a search found, as a date: 1 January of it.
export function birthDateFromYear(year) {
  const y = Number(year)
  return Number.isInteger(y) && y >= 1900 && y <= 2100 ? `${y}-01-01` : ""
}

// The list with the entry at `index` swapped with its neighbour above (-1)
// or below (+1); unchanged at either end.
export function moveBoard(list, index, step) {
  const to = index + step
  if (to < 0 || to >= list.length) return list.slice()
  const out = list.slice()
  ;[out[index], out[to]] = [out[to], out[index]]
  return out
}

const RATING_FIELD = { Std: "fide_rating_standard", Rapid: "fide_rating_rapid", Blitz: "fide_rating_blitz" }

// The rating that counts: the tournament's own time control's, else standard.
export function effectiveRating(r, trn) {
  const own = Number(r[RATING_FIELD[trn && trn.time_control] || "fide_rating_standard"])
  if (own > 0) return own
  const std = Number(r.fide_rating_standard)
  return std > 0 ? std : null
}

// The teams of a team tournament for the public list, by name: each with
// its players on the boards in board order, its reserves after them, the
// club most of its players are in, and the average rating of its boards
// (null when none of them is rated).
export function teamsForList(registrations, teams, trn) {
  const size = Number(trn && trn.team_size) || 0
  const byTeam = new Map(teams.map((tm) => [tm.id, []]))
  for (const r of registrations) {
    if (byTeam.has(r.team_id)) byTeam.get(r.team_id).push(r)
  }
  return teams
    .slice()
    .sort((a, b) => String(a.name || "").localeCompare(String(b.name || "")) || a.id - b.id)
    .map((tm) => {
      const players = byTeam.get(tm.id).slice().sort((a, b) => (a.team_board || 0) - (b.team_board || 0) || a.id - b.id)
      const boards = size > 0 ? players.slice(0, size) : players
      const reserves = size > 0 ? players.slice(size) : []
      const clubs = new Map()
      for (const p of players) {
        const c = Number(p.national_club)
        if (c > 0) clubs.set(c, (clubs.get(c) || 0) + 1)
      }
      let club = null
      for (const [c, n] of clubs) if (club === null || n > clubs.get(club)) club = c
      const ratings = boards.map((p) => effectiveRating(p, trn)).filter((v) => v)
      const rating = ratings.length ? Math.round(ratings.reduce((a, b) => a + b, 0) / ratings.length) : null
      return { id: tm.id, name: tm.name, club, rating, boards, reserves }
    })
}

// The first empty board slot with a filled one after it, or -1. The form
// sends the filled slots only, so a gap moved every player after it up a
// board and the server's "board 3" named the wrong box (bug scan, 26 Nov
// 2026). Empty slots at the end are fine: a team may register short.
export function teamGap(players, filled) {
  let empty = -1
  for (let i = 0; i < players.length; i++) {
    if (!filled(players[i])) {
      if (empty === -1) empty = i
    } else if (empty !== -1) {
      return empty
    }
  }
  return -1
}

// The category after the birth year changed: `index` is the one the year
// fits (null for none). A category picked by hand stays; one picked from
// the year follows it, and goes when the year fits none (it used to stay,
// and the server kept a category that did not fit).
export function autoCategory({ current, auto, index }) {
  const picked = current !== "" && current !== null && current !== undefined
  if (picked && !auto) return { category_index: current, auto: false }
  if (index === null || index === undefined) return { category_index: "", auto: false }
  return { category_index: index, auto: true }
}

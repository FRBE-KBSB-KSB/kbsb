// Tournament registration categories as the form shows them: the organiser's
// label and the birth years a category takes ("Pupillen (2018 of later)"),
// next to the value SWAR gets. The API works the ranges out
// (category_ranges, see kbsb-dataplatform's categoryRanges()); a tournament
// row without them, from before they existed, shows its categories as they
// are.

export function categoryRanges(trn) {
  if (!trn) return []
  if (Array.isArray(trn.category_ranges) && trn.category_ranges.length) return trn.category_ranges
  const cats = Array.isArray(trn.categories) ? trn.categories : []
  return cats.map((c, i) => ({ index: i, value: String(c), label: String(c), birth_year_from: null, birth_year_to: null }))
}

// "Pupillen (2018 of later)", "Pionnen (2016-2017)", or the label alone.
export function categoryDisplay(range, t) {
  if (!range) return ""
  const from = range.birth_year_from
  const to = range.birth_year_to
  if (from != null && to != null) return `${range.label} (${from === to ? from : `${from}-${to}`})`
  if (from != null) return `${range.label} (${t("trnreg.year_or_later", { year: from })})`
  if (to != null) return `${range.label} (${t("trnreg.year_or_earlier", { year: to })})`
  return range.label
}

// The category a birth year falls in, or null: the narrowest range that takes
// it, as the API picks one when the form sends none.
export function categoryForBirthYear(trn, year) {
  const y = Number(year)
  if (!Number.isInteger(y) || y <= 0) return null
  let best = null
  let bestSpan = Infinity
  for (const r of categoryRanges(trn)) {
    if (r.birth_year_from == null && r.birth_year_to == null) continue
    if (r.birth_year_from != null && y < r.birth_year_from) continue
    if (r.birth_year_to != null && y > r.birth_year_to) continue
    const span = (r.birth_year_to == null ? 2100 : r.birth_year_to) - (r.birth_year_from == null ? 1900 : r.birth_year_from)
    if (span < bestSpan) {
      best = r.index
      bestSpan = span
    }
  }
  return best
}

// The birth year a player's details give: the date typed, else the year the
// search found.
export function birthYearOf(player) {
  const m = String((player && player.date_birth) || "").match(/^(\d{4})-/)
  if (m) return Number(m[1])
  const y = Number(player && player.birth_year)
  return Number.isInteger(y) && y > 0 ? y : null
}

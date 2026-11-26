// The tournament registration form's own logic, after Luc's remarks of 26 Nov
// 2026. Run with `node --test tests/*.test.mjs` from frontend/.

import test from "node:test"
import assert from "node:assert/strict"
import {
  isSingleDay,
  spreadRoundDates,
  parseBirthInput,
  formatBirthInput,
  birthDateFromYear,
  moveBoard,
  teamsForList,
  teamGap,
  autoCategory,
} from "../util/trnreg_form.js"

test("a tournament of one day, or without an end date, is a single day", () => {
  assert.equal(isSingleDay("2026-12-18", "2026-12-18"), true)
  assert.equal(isSingleDay("2026-12-18", ""), true)
  assert.equal(isSingleDay("2026-12-18", null), true)
  assert.equal(isSingleDay("2026-12-18", "2026-12-20"), false)
  assert.equal(isSingleDay("", ""), false)
})

test("one per day never goes past the end date", () => {
  // 18/12 to 18/12, 15 rounds: every round on the 18th, not up to 1 January.
  const one = spreadRoundDates("2026-12-18", "2026-12-18", 15)
  assert.equal(one.length, 15)
  assert.ok(one.every((d) => d === "2026-12-18"))
  // No end date is the same single day.
  assert.ok(spreadRoundDates("2026-12-18", "", 3).every((d) => d === "2026-12-18"))
  // As many days as rounds: one a day.
  assert.deepEqual(spreadRoundDates("2026-12-18", "2026-12-20", 3), ["2026-12-18", "2026-12-19", "2026-12-20"])
  // Fewer days than rounds: several a day, in order, the first days fullest.
  assert.deepEqual(spreadRoundDates("2026-12-05", "2026-12-06", 5), ["2026-12-05", "2026-12-05", "2026-12-05", "2026-12-06", "2026-12-06"])
  // More days than rounds: one a day from the start, as before.
  assert.deepEqual(spreadRoundDates("2026-12-05", "2026-12-31", 3), ["2026-12-05", "2026-12-06", "2026-12-07"])
  // Across the year end.
  assert.deepEqual(spreadRoundDates("2026-12-31", "2027-01-01", 2), ["2026-12-31", "2027-01-01"])
  assert.deepEqual(spreadRoundDates("", "", 3), [])
  assert.deepEqual(spreadRoundDates("2026-12-18", "2026-12-18", 0), [])
})

test("a birth date is typed as a day or as a year alone", () => {
  assert.equal(parseBirthInput("2009"), "2009-01-01")
  assert.equal(parseBirthInput(" 2009 "), "2009-01-01")
  assert.equal(parseBirthInput("04/03/2009"), "2009-03-04")
  assert.equal(parseBirthInput("4/3/2009"), "2009-03-04")
  assert.equal(parseBirthInput("4-3-2009"), "2009-03-04")
  assert.equal(parseBirthInput("04.03.2009"), "2009-03-04")
  assert.equal(parseBirthInput("2009-03-04"), "2009-03-04")
  assert.equal(parseBirthInput(""), "")
  for (const bad of ["31/02/2009", "2009-13-01", "abc", "1/1/09", "1850", "3000"]) {
    assert.equal(parseBirthInput(bad), null, bad)
  }
  assert.equal(formatBirthInput("2009-03-04"), "04/03/2009")
  assert.equal(formatBirthInput("2009-03-04T00:00:00.000Z"), "04/03/2009")
  assert.equal(formatBirthInput(""), "")
})

test("a year the search found becomes 1 January of it", () => {
  assert.equal(birthDateFromYear(2010), "2010-01-01")
  assert.equal(birthDateFromYear("2010"), "2010-01-01")
  assert.equal(birthDateFromYear(null), "")
  assert.equal(birthDateFromYear(0), "")
})

test("a board moves up or down, swapping with its neighbour", () => {
  assert.deepEqual(moveBoard(["a", "b", "c"], 2, -1), ["a", "c", "b"])
  assert.deepEqual(moveBoard(["a", "b", "c"], 0, 1), ["b", "a", "c"])
  assert.deepEqual(moveBoard(["a", "b", "c"], 0, -1), ["a", "b", "c"])
  assert.deepEqual(moveBoard(["a", "b", "c"], 2, 1), ["a", "b", "c"])
})

test("the public list of a team tournament shows teams, players by board, reserves apart", () => {
  const trn = { team_tournament: true, team_size: 2, time_control: "Std" }
  const regs = [
    { id: 1, last_name: "Reserve", first_name: "R", team_id: 5, team_board: 3, national_club: 703, fide_rating_standard: 1000 },
    { id: 2, last_name: "Eerste", first_name: "E", team_id: 5, team_board: 1, national_club: 703, fide_rating_standard: 1800 },
    { id: 3, last_name: "Tweede", first_name: "T", team_id: 5, team_board: 2, national_club: 714, fide_rating_standard: 1600 },
    { id: 4, last_name: "Alleen", first_name: "A", team_id: 6, team_board: 1, national_club: 714 },
  ]
  const teams = teamsForList(regs, [{ id: 6, name: "Zwart" }, { id: 5, name: "Antwerpen" }], trn)
  assert.deepEqual(teams.map((t) => t.name), ["Antwerpen", "Zwart"])
  const a = teams[0]
  assert.deepEqual(a.boards.map((r) => r.id), [2, 3])
  assert.deepEqual(a.reserves.map((r) => r.id), [1])
  // The club most of its players are in, and the boards' average rating.
  assert.equal(a.club, 703)
  assert.equal(a.rating, 1700)
  assert.equal(teams[1].rating, null)
  assert.equal(teams[1].boards.length, 1)
})

// Bug scan of 26 Nov 2026.

test("a filled board after an empty one is a gap; empty boards at the end are not", () => {
  const filled = (p) => !!p.last_name
  assert.equal(teamGap([{ last_name: "A" }, { last_name: "" }, { last_name: "C" }], filled), 1)
  assert.equal(teamGap([{ last_name: "" }, { last_name: "B" }], filled), 0)
  assert.equal(teamGap([{ last_name: "A" }, { last_name: "B" }, { last_name: "" }, { last_name: "" }], filled), -1)
  assert.equal(teamGap([], filled), -1)
})

test("a category picked from the birth year goes when the year fits no category", () => {
  // Picked automatically, the year now fits none: cleared.
  assert.deepEqual(autoCategory({ current: 3, auto: true, index: null }), { category_index: "", auto: false })
  // Picked automatically, the year fits another: that one.
  assert.deepEqual(autoCategory({ current: 3, auto: true, index: 1 }), { category_index: 1, auto: true })
  // Nothing picked yet: the one the year fits, or still nothing.
  assert.deepEqual(autoCategory({ current: "", auto: false, index: 2 }), { category_index: 2, auto: true })
  assert.deepEqual(autoCategory({ current: "", auto: false, index: null }), { category_index: "", auto: false })
  // Picked by hand: kept, whatever the year.
  assert.deepEqual(autoCategory({ current: 0, auto: false, index: null }), { category_index: 0, auto: false })
  assert.deepEqual(autoCategory({ current: 0, auto: false, index: 2 }), { category_index: 0, auto: false })
})

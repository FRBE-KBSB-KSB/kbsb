export const PLAYERSTATUS = {
  assigned: "assigned",
  locked: "locked",
  exported: "exported",
  imported: "imported",
  unassigned: "unassigned",
}
export const EMPTY_VENUE = {
  address: "",
  available: "all",
  notavailable: [],
  capacity: 99,
  email: "",
  phone: "",
}

export const resultchoices = [
  { title: "not played", value: "" },
  { title: "1-0", value: "1-0" },
  { title: "½-½", value: "½-½" },
  { title: "0-1", value: "0-1" },
  { title: "1-0 FF", value: "1-0 FF" },
  { title: "0-1 FF", value: "0-1 FF" },
]

export const overrulechoices = [
  { title: "not played", value: "" },
  { title: "not overruled", value: "NOR" },
  { title: "1-0", value: "1-0" },
  { title: "½-½", value: "½-½" },
  { title: "0-1", value: "0-1" },
  { title: "1-0 FF", value: "1-0 FF" },
  { title: "0-1 FF", value: "0-1 FF" },
  { title: "0-0 FF", value: "0-0 FF" },
  { title: "½-0", value: "½-0" },
  { title: "0-½", value: "0-½" },
  { title: "Team FF", value: "Team FF" },
]

export function round_selector(icdata) {
  console.log("round_selector", icdata.rounds11)
  const sel_array = Object.entries(icdata.rounds11).map(([round, date]) => {
    if (round <= 5) {
      return { value: round, title: `${date}:  R${round}` }
    } else if (round > 7) {
      return { value: round, title: `${date}:  R${round}  (R${round - 2} Div. 6)` }
    }
    return { value: round, title: `${date}:  R${round}  (No Div. 6)` }
  })
  return sel_array
}

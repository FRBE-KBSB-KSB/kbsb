export const CLUB_STATUS = {
  CONSULTING: 0,
  MODIFYING: 1,
}

export const EMPTY_BOARD = {
  president: { idnumber: 0 },
  vice_president: { idnumber: 0 },
  secretary: { idnumber: 0 },
  treasurer: { idnumber: 0 },
  tournament_director: { idnumber: 0 },
  youth_director: { idnumber: 0 },
  interclub_director: { idnumber: 0 },
  webmaster: { idnumber: 0 },
  bar_manager: { idnumber: 0 },
  press_officer: { idnumber: 0 },
  material_manager: { idnumber: 0 },
}

export const visibility_items = [
  { title: "Hidden", value: "HIDDEN" },
  { title: "Club", value: "CLUB" },
  { title: "Public", value: "PUBLIC" },
]

export const EMPTY_CLUB = {
  venue: "",
  address: "",
  openinghours: {},
}

export const ROLES = ["ClubAdmin", "InterclubAdmin"]

export const INTERCLUBS_STATUS = {
  CONSULTING: 0,
  MODIFYING: 1,
};

export const empty_enrollment = {
  teams1: 0,
  teams2: 0,
  teams3: 0,
  teams4: 0,
  teams5: 0,
  wishes: {},
};

export const STOPDATE = new Date("2023-08-05");

export const INTERCLUBS_ROUNDS = {
  1: "2023-09-24",
  2: "2023-10-15",
  3: "2023-10-22",
  4: "2023-11-19",
  5: "2023-12-03",
  6: "2024-01-28",
  7: "2024-02-04",
  8: "2024-02-18",
  9: "2024-03-10",
  10: "2024-03-24",
  11: "2024-04-21",
};

export const PLAYERS_DIVISION = {
  1: 8,
  2: 8,
  3: 6,
  4: 4,
  5: 4,
};

export const PLAYERSTATUS = {
  assigned: "assigned",
  unassigned: "unassigned",
  requestedout: "requestedout",
  requestedin: "requestedin",
  comfirmedin: "confirnedin",
  confirmedout: "confirmedout",
  locked: "locked",
};
export const EMPTY_VENUE = {
  address: "",
  available: "all",
  notavailable: [],
  capacity: 99,
  email: "",
  phone: "",
};

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

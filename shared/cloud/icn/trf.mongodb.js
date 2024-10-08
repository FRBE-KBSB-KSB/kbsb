// Select the database to use.
use("kbsb")

// find ruben decrop
db.getCollection("ic2324trf").findOne({ idbel: 45608 })

// copy collection
// sb is source db
db.interclub2425venues.find().forEach(function (d) {
  db.getSiblingDB("kbsblocal")["interclub2425venues"].insert(d)
})

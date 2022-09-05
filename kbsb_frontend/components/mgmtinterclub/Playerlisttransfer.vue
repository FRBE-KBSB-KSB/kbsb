<template>
  <div>
    <div class="mt-2">
      <h4>Incoming transfers</h4>
      <v-data-table :headers="trinheaders" :items="transfersin">
      </v-data-table>
      <div>
        Creating a new transfer request:
        <v-text-field v-model="transferin" label="ID number" />
        <v-btn @click="addTransferIn">Add</v-btn>
      </div>
    </div>
    <div class="mt-2">
      <h4>Outgoing transfers</h4>
      <v-data-table :headers="troutheaders" :items="transfersout">
      </v-data-table>
    </div>
    <div class="mt-2" v-if="teams.length">
      <v-btn color="deep-purple" class="white--text" @click="next">
        Continue
      </v-btn>
      <v-btn @click="prev">
        Back
      </v-btn>
    </div>
  </div>
</template>

<script>

export default {
  data() {
    return {
      nmheaders: [
        { text: "First name", value: "first_name", sortable: true },
        { text: "Last name", value: "last_name", sortable: true },
        { text: "ID number", value: "idnumber", sortable: false },
        { text: "Club ID", value: "idclub", sortable: true },
        { text: "Nat. Elo", value: "natrating", sortable: true },
        { text: "Fide Elo", value: "fiderating", sortable: true },
        { text: 'Actions', value: 'actions', sortable: false },
      ],
      plheaders: [
        { text: "First name", value: "first_name", sortable: true },
        { text: "Last name", value: "last_name", sortable: true },
        { text: "ID number", value: "idnumber", sortable: false },
        { text: "Club ID", value: "idclub", sortable: true },
        { text: "Nat. Elo", value: "natrating", sortable: true },
        { text: "Fide Elo", value: "fiderating", sortable: true },
      ],
      trinheaders: [
        { text: "First name", value: "first_name", sortable: true },
        { text: "Last name", value: "last_name", sortable: true },
        { text: "ID number", value: "idnumber", sortable: false },
        { text: "From club", value: "idclub", sortable: false },
        { text: "Nat. Elo", value: "natrating", sortable: true },
        { text: "Fide Elo", value: "fiderating", sortable: true },
        { text: "Confirmed", value: "transfer_confirmed", sortable: false },
      ],
      troutheaders: [
        { text: "First name", value: "first_name", sortable: true },
        { text: "Last name", value: "last_name", sortable: true },
        { text: "ID number", value: "idnumber", sortable: false },
        { text: "To club", value: "idvisitingclub", sortable: false },
        { text: "Confirmed", value: "confirmed_date", sortable: false },
      ],
      transferin: ""

    }
  },

  props: {
    club: Object,
    activenotloaded: Boolean,
  },

  computed: {
    step() {
      return this.$store.state.mgmtplayerlist.step
    },
    players() {
      return this.$store.state.mgmtplayerlist.players
    },
    teams() {
      return this.$store.state.mgmtplayerlist.teams
    },
    transfersin() {
      return this.players.filter(x => x.transfer)
    },
    transfersout() {
      return this.$store.state.mgmtplayerlist.transfersout
    },
  },

  methods: {

    addMember(x) {
      const players = [...this.players]
      players.push({
        fiderating: x.fiderating,
        first_name: x.first_name,
        idnumber: x.idnumber,
        idclub: x.idclub,
        last_name: x.last_name,
        natrating: x.natrating,
        transfer: false
      })
      this.$store.commit('mgmtplayerlist/updatePlayers', players)
    },

    addAllMembers() {
      const players = [...this.players]
      this.newmembers.forEach(x => players.push({
        fiderating: x.fiderating,
        first_name: x.first_name,
        idnumber: x.idnumber,
        idclub: x.idclub,
        last_name: x.last_name,
        natrating: x.natrating,
        transfer: false
      }))
      this.$store.commit('mgmtplayerlist/updatePlayers', players)
    },

    async addTransferIn() {
      try {
        const reply = await this.$api.old.get_member({
          idnumber: this.transferin,
        })
        this.transferin = ""
        const pl = reply.data
        const players = [...this.players]
        players.push({
          fiderating: pl.fiderating,
          first_name: pl.first_name,
          idnumber: pl.idnumber,
          idclub: pl.idclub,
          last_name: pl.last_name,
          natrating: pl.natrating,
          transfer: true
        })
      } catch (error) {
        switch (reply.status) {
          case 400:
            this.$root.$emit('snackbar', { text: this.$t('Invalid id') })
            break
          case 404:
            this.$root.$emit('snackbar', { text: this.$t('Player not found') })
            break
          default:
            console.error('Getting member failed', reply.data.detail)
            this.$root.$emit('snackbar', { text: this.$t('Getting member failed') })
        }
      }
    },

    next() {
      this.$store.commit('mgmtplayerlist/updateStep', this.step + 1)
    },

    prev() {
      this.$store.commit('mgmtplayerlist/updateStep', this.step - 1)
    }
  }
}
</script>


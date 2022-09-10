<template>
  <div>

    <div v-if="!teams.length">
      <h3 class="my-2">Active players of club {{ club.idclub }}</h3>
      <v-data-table :headers="amheaders" :items="activemembers" :loading="activenotloaded"
        loading-text="Loading members ... Please wait" :footer-props="footerProps">
        <template #:no-data>No new members found</template>
      </v-data-table>
    </div>

    <div v-if="teams.length">
      <h4 class="my-2">Incoming transfers</h4>
      <v-data-table :headers="trinheaders" :items="transfersin" :footer-props="footerProps">
        <template #no-data>No incoming transfers</template>
      </v-data-table>
      <v-card color="#f4f4f4">
        <v-card-title>
          Add a transfer from a club:
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-row>
            <v-col cols="5" sm="3">
              <v-text-field v-model="plin" label="ID number" />
            </v-col>
            <v-col col="2" sm="1">
              <v-btn fab outlined color="deep-purple" @click="trin_one">
                <v-icon>mdi-transfer-right</v-icon>
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </div>

    <h3 class="my-2">Outgoing transfers</h3>
    <v-data-table :headers="troutheaders" :items="transfersout">
      <template #no-data>No outgoing transfers</template>
    </v-data-table>

    <v-card v-if="!teams.length" color="#f4f4f4">
      <v-card-title>
        Transfer of all members to a single club at once
      </v-card-title>
      <v-divider />
      <v-card-text>
        <v-row>
          <v-col cols="5" sm="3">
            <v-text-field label="Number club" v-model="tr_cluball" />
          </v-col>
          <v-col col="2" sm="1">
            <v-btn fab outlined color="deep-purple" @click="trout_all">
              <v-icon>mdi-transfer-right</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-card color="#f4f4f4">
      <v-card-title>
        Add transfer to a club
      </v-card-title>
      <v-divider />
      <v-card-text>
        <v-row>
          <v-col col="5" sm="3">
            <v-text-field v-model="plout" label="ID number"></v-text-field>
          </v-col>
          <v-col col="5" sm="3">
            <v-text-field label="Number club" v-model="tr_clubone" />
          </v-col>
          <v-col col="2" sm="1">
            <v-btn fab outlined color="deep-purple" @click="trout_one">
              <v-icon>mdi-transfer-right</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <div class="my-3" v-if="teams.length">
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
      amheaders: [
        { text: "First name", value: "first_name", sortable: true },
        { text: "Last name", value: "last_name", sortable: true },
        { text: "ID number", value: "idnumber", sortable: false },
        { text: "Nat. Elo", value: "natrating", sortable: true },
        { text: "Fide Elo", value: "fiderating", sortable: true },
      ],
      plout: "",
      plin: "",
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
      tr_cluball: "",
      tr_clubone: "",
      footerProps: {
        itemsPerPageOptions: [30, 60, -1],
        itemsPerPage: 30
      },
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
    activemembers() {
      return this.$store.state.mgmtplayerlist.activemembers
    },
    transfersout() {
      return this.$store.state.mgmtplayerlist.transfersout
    },
    transfersin() {
      return this.players.filter(x => x.transfer)
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

    trout_all() {
      const transfersout = [...this.transfersout]
      const now = new Date()
      this.activemembers.forEach((x) => {
        transfersout.push({
          first_name: x.first_name,
          idnumber: x.idnumber,
          idoriginalclub: this.club.idclub,
          idvisitingclub: this.tr_cluball,
          last_name: x.last_name,
          confirmed_date: now,
          request_date: now,
        })
      })
      this.$store.commit('mgmtplayerlist/updateTransfersout', transfersout)
      this.tr_cluball = ''
    },

    trout_one() {
      const transfersout = [...this.transfersout]
      const now = new Date()
      const pl = this.activemembers.find(x => x.idnumber == this.plout)
      if (!pl) {
        this.$root.$emit('snackbar', { text: this.$t('Cannot add: not a member of the club') })
        return
      }
      transfersout.push({
        first_name: pl.first_name,
        idnumber: this.plout,
        idoriginalclub: this.club.idclub,
        idvisitingclub: this.tr_clubone,
        last_name: pl.last_name,
        confirmed_date: now,
        request_date: now,
      })
      this.$store.commit('mgmtplayerlist/updateTransfersout', transfersout)
      this.plout = ''
      this.tr_clubone = ''
    },

    async trin_one() {
      try {
        const reply = await this.$api.old.get_member({
          idnumber: this.plin,
        })
        this.trin = ""
        const pl = reply.data
        console.log('pl', pl)
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
        this.$store.commit('mgmtplayerlist/updatePlayers', players)
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


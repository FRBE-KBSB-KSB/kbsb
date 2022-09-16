<template>
  <div>

    <div v-if="!teams.length">
      <h3 class="my-2">{{ $t('Active players of club') }} {{ club.idclub }}</h3>
      <v-data-table :headers="amheaders" :items="activemembers" :loading="activenotloaded"
        loading-text="Loading members ... Please wait" :footer-props="footerProps">
        <template v-slot:item.ix="{ item }">
          {{ activemembers.indexOf(item) + 1 }} 
        </template>
        <template #:no-data>No new members found</template>
      </v-data-table>
    </div>

    <div v-if="teams.length">
      <h4 class="my-2">{{ $t('Incoming transfers') }}</h4>
      <v-data-table :headers="trinheaders" :items="transfersin" :footer-props="footerProps">
        <template v-slot:item.ix="{ item }">
          {{ transfersin.indexOf(item) + 1 }} 
        </template>
        <template #no-data>{{ $t('No incoming transfers') }}</template>
        <template #item.action="{ item }">
          <v-tooltip bottom>
            <template #activator="{ on }">
              <v-icon small outline class="mr-2" v-on="on" @click="rmTransferin(item)">
                mdi-minus
              </v-icon>
            </template>
            {{ $t('Remove transfer') }}
          </v-tooltip>
        </template>
      </v-data-table>
      <v-card color="#f4f4f4">
        <v-card-title>
          {{ $t('Add a transfer from a club') }}
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-row>
            <v-col cols="5" sm="3">
              <v-text-field v-model="plin" label="ID number" />
            </v-col>
            <v-col col="2" sm="1">
              <v-btn fab outlined color="green" @click="trin_one">
                <v-icon>mdi-transfer-right</v-icon>
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </div>

    <h4 class="my-2">{{ $t('Outgoing transfers') }}</h4>
    <v-data-table :headers="troutheaders" :items="transfersout">
      <template v-slot:item.ix="{ item }">
        {{ transfersout.indexOf(item) + 1 }} 
      </template>
      <template #no-data>{{ $t('No outgoing transfers') }}</template>
      <template #item.action="{ item }">
        <v-tooltip bottom>
          <template #activator="{ on }">
            <v-icon small outline class="mr-2" v-on="on" @click="rmTransferout(item)">
              mdi-minus
            </v-icon>
          </template>
          {{ $t('Remove transfer') }}
        </v-tooltip>
      </template>
    </v-data-table>

    <v-card v-if="!teams.length" color="#f8f8f8">
      <v-card-title>
        {{ $t('Transfer of all members to a single club at once.') }}
      </v-card-title>
      <v-divider />
      <v-card-text>
        <v-row>
          <v-col cols="5" sm="3">
            <v-text-field label="Number club" v-model="tr_cluball" />
          </v-col>
          <v-col col="2" sm="1">
            <v-btn fab outlined color="green" @click="trout_all">
              <v-icon>mdi-transfer-right</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-card color="#f8f8f8">
      <v-card-title>
        {{ $t('Add transfer to a club') }}
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
            <v-btn fab outlined color="green" @click="trout_one">
              <v-icon>mdi-transfer-right</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <div class="my-3" v-if="teams.length">
      <v-btn color="green" class="white--text" @click="next">
        {{ $t('Continue') }}
      </v-btn>
      <v-btn @click="prev">
        {{ $t('Back') }}
      </v-btn>
    </div>

  </div>
</template>

<script>

export default {
  data() {
    return {
      amheaders: [
        { text: '#', value: 'ix', sortable: false },
        { text: this.$t("First name"), value: "first_name", sortable: true },
        { text: this.$t("Last name"), value: "last_name", sortable: true },
        { text: this.$t("ID number"), value: "idnumber", sortable: false },
        { text: "Nat. Elo", value: "natrating", sortable: true },
        { text: "Fide Elo", value: "fiderating", sortable: true },
      ],
      plout: "",
      plin: "",
      trinheaders: [
        { text: '#', value: 'ix', sortable: false },
        { text: this.$t("First name"), value: "first_name", sortable: true },
        { text: this.$t("Last name"), value: "last_name", sortable: true },
        { text: this.$t("ID number"), value: "idnumber", sortable: false },
        { text: this.$t("From club"), value: "idclub", sortable: false },
        { text: "Nat. Elo", value: "natrating", sortable: true },
        { text: "Fide Elo", value: "fiderating", sortable: true },
        { text: this.$t("Confirmed"), value: "transfer_confirmed", sortable: false },
        { text: this.$t("Actions"), value: "action", sortable: false },

      ],
      troutheaders: [
        { text: '#', value: 'ix', sortable: false },
        { text: "First name", value: "first_name", sortable: true },
        { text: "Last name", value: "last_name", sortable: true },
        { text: "ID number", value: "idnumber", sortable: false },
        { text: "To club", value: "idvisitingclub", sortable: false },
        { text: "Confirmed", value: "confirmed_date", sortable: false },
        { text: this.$t("Actions"), value: "action", sortable: false },
      ],
      tr_cluball: "",
      tr_clubone: "",
      footerProps: {
        itemsPerPageOptions: [30, 60, -1],
        itemsPerPage: 30
      }
    }
  },

  props: {
    club: Object,
    activenotloaded: Boolean,
  },

  computed: {
    step() {
      return this.$store.state.playerlist.step
    },
    players() {
      return this.$store.state.playerlist.players
    },
    teams() {
      return this.$store.state.playerlist.teams
    },
    activemembers() {
      return this.$store.state.playerlist.activemembers
    },
    transfersout() {
      return this.$store.state.playerlist.transfersout
    },
    transfersin() {
      return this.players.filter(x => x.transfer)
    },
  },

  methods: {

    rmTransferin(it) {
      console.log('remove', it)
      const pls = [...this.players]
      pls.some((x, ix) => {
        if (x.idnumber == it.idnumber) {
          console.log('found player', x.idnumber)
          pls.splice(ix, 1)
          return true
        }
      })
      this.$store.commit('playerlist/updatePlayers', pls)
    },


    rmTransferout(it) {
      const trout = [...this.transfersout]
      trout.some((x, ix) => {
        console.log("x", x.idnumber)
        if (x.idnumber == it.idnumber) {
          trout.splice(ix, 1)
          return true
        }
      })
      this.$store.commit('playerlist/updateTransfersout', trout)
      const pl = this.activemembers.find(x => x.idnumber == it.idnumber)
      if (!pl) {
        console.log('it is not an active member, so not added to playerlist')
        return
      }
      console.log('pl', pl.idnumber, pl.assignedrating)
      this.$root.$emit('addmember', pl)
      console.log('last player', this.players[this.players.length-1])
      this.$root.$emit('buildplayers')
    },

    rmDoubles() {
      const plys = []
      const ids = new Set()
      this.players.forEach((x) => {
        if (ids.has(x.idnumber)) {
          return
        }
        plys.push(x)
      })
      this.$store.commit('playerlist/updatePlayers', plys)
    },

    rmTransfersoutFromPlayerslist() {
      const pls = []
      const ids = new Set()
      this.transfersout.forEach((x) => ids.add(x.idnumber))
      this.players.forEach((p, ix) => {
        if (ids.has(p.idnumber)) {
          return
        }
        pls.push(p)
      })
      this.$store.commit('playerlist/updatePlayers', pls)
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
      this.$store.commit('playerlist/updateTransfersout', transfersout)
      this.rmTransfersoutFromPlayerslist()
      this.tr_cluball = ''
    },

    trout_one() {
      let plid, clid
      try {
        plid = parseInt(this.plout)
      } catch (error) {
        this.$root.$emit('snackbar', { text: this.$t('Invalid ID number') })
        return
      }
      try {
        clid = parseInt(this.tr_clubone)
      } catch (error) {
        this.$root.$emit('snackbar', { text: this.$t('Invalid club number') })
        return
      }
      const transfersout = [...this.transfersout]
      const now = new Date()
      const pl = this.activemembers.find(x => x.idnumber == plid)
      if (!pl) {
        this.$root.$emit('snackbar', { text: this.$t('Cannot add: not a member of the club') })
        return
      }
      transfersout.push({
        first_name: pl.first_name,
        idnumber: plid,
        idoriginalclub: this.club.idclub,
        idvisitingclub: clid,
        last_name: pl.last_name,
        confirmed_date: now,
        request_date: now,
      })
      this.$store.commit('playerlist/updateTransfersout', transfersout)
      this.rmTransfersoutFromPlayerslist()
      this.plout = ''
      this.tr_clubone = ''
    },

    async trin_one() {
      let pl;
      const pids = new Set()
      this.players.forEach(x => pids.add(x.idnumber))
      if (pids.has(this.plin)) {
        this.$root.$emit('snackbar', { text: this.$t('Player already in playerlist') })
        return
      }
      try {
        const reply = await this.$api.old.get_member({
          idnumber: this.plin,
        })
        console.log('reply', reply)
        pl = reply.data
      } catch (error) {
        this.$root.$emit('snackbar', { text: this.$t('Unknonw player') })
        return
      }
      this.plin = ""
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
      this.$store.commit('playerlist/updatePlayers', players)
    },

    next() {
      this.$store.commit('playerlist/updateStep', this.step + 1)
    },

    prev() {
      this.$store.commit('playerlist/updateStep', this.step - 1)
    }
  }
}
</script>


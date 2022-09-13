<template>
  <div>
    <div class="mt-2">
      <h4>Active players of club {{ club.idclub }} not on the playerlist </h4>
      <div>These members can automatically be added to the playerlist.
        <v-btn class="ml-2" @click="addAllMembers">Add all</v-btn>
      </div>
      <v-data-table :headers="nmheaders" :items="newmembers" :loading="activenotloaded"
        loading-text="Loading members ... PLease wait" :footer-props="footerProps">
        <template v-slot:item.ix="{ item }">
          {{ newmembers.indexOf(item) + 1 }} 
        </template>
        <template #:no-data>No new members found</template>
        <template v-slot:item.actions="{ item }">
          <v-tooltip bottom>
            <template #activator="{ on }">
              <v-icon small outline class="mr-2" v-on="on" @click="addMember(item)">
                mdi-plus
              </v-icon>
            </template>
            Add to playerlist
          </v-tooltip>
        </template>
      </v-data-table>
    </div>
    <div class="mt-2" v-show="ownplayers.length">
      <h4>Own players on the playerlist</h4>
      <v-data-table :headers="plheaders" :items="ownplayers" :footer-props="footerProps">
        <template v-slot:item.ix="{ item }">
          {{ ownplayers.indexOf(item) + 1 }} 
        </template>
      </v-data-table>
    </div>
    <div class="mt-2">
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
        { text: '#', value: 'ix', sortable: false },
        { text: "First name", value: "first_name", sortable: true },
        { text: "Last name", value: "last_name", sortable: true },
        { text: "ID number", value: "idnumber", sortable: false },
        { text: "Club ID", value: "idclub", sortable: true },
        { text: "Nat. Elo", value: "natrating", sortable: true },
        { text: "Fide Elo", value: "fiderating", sortable: true },
        { text: 'Actions', value: 'actions', sortable: false },
      ],
      plheaders: [
        { text: '#', value: 'ix', sortable: false },
        { text: "First name", value: "first_name", sortable: true },
        { text: "Last name", value: "last_name", sortable: true },
        { text: "ID number", value: "idnumber", sortable: false },
        { text: "Club ID", value: "idclub", sortable: true },
        { text: "Nat. Elo", value: "natrating", sortable: true },
        { text: "Fide Elo", value: "fiderating", sortable: true },
      ],
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
    activemembers() {
      return this.$store.state.mgmtplayerlist.activemembers
    },
    newmembers() {
      const pl = new Set()
      this.players.forEach((x) => pl.add(x.idnumber))
      return this.activemembers.filter(x => !pl.has(x.idnumber))
    },
    players() {
      return this.$store.state.mgmtplayerlist.players
    },
    ownplayers() {
      return this.players.filter(x => !x.transfer)
    },
    transfersin() {
      return this.players.filter(x => x.transfer)
    },
    transfersout() {
      return this.$store.state.mgmtplayerlist.transfersout
    },
  },

  methods: {

    addMember(p) {
      this.$root.$emit('addmember', p)
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


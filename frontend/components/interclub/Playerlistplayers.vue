<template>
  <div>
    <div class="mt-2">
      <h4>{{ $t('Active players of club') }} {{ club.idclub }}, {{ $t('not on the playerlist.') }}
      </h4>
      <div>{{ $t('These members can automatically be added to the playerlist.') }}
        <v-btn class="ml-2" @click="addAllMembers">Add all</v-btn>
      </div>
      <v-data-table :headers="nmheaders" :items="newmembers" :loading="activenotloaded"
          :loading-text="$t('Loading members ... Please wait')" :footer-props="footerProps">
        <template v-slot:item.ix="{ item }">
          {{ newmembers.indexOf(item) + 1 }} 
        </template>
        <template #:no-data>{{ $t('No new members found') }}</template>
        <template v-slot:item.actions="{ item }">
          <v-tooltip bottom>
            <template #activator="{ on }">
              <v-icon small outline class="mr-2" v-on="on" @click="addMember(item)">
                mdi-plus
              </v-icon>
            </template>
            {{ $t('Add to playerlist') }}
          </v-tooltip>
        </template>
      </v-data-table>
    </div>
    <div class="mt-2" v-show="ownplayers.length">
      <h4>{{ $t('Own players on the playerlist') }}</h4>
      <v-data-table :headers="plheaders" :items="ownplayers" :footer-props="footerProps">
        <template v-slot:item.actions="{ item }">
          <v-tooltip bottom>
            <template #activator="{ on }">
              <v-icon small outline class="mr-2" v-on="on" @click="removeMember(item)">
                mdi-minus
              </v-icon>
            </template>
            {{ $t('Remove from playerlist') }}
          </v-tooltip>
        </template>
        <template v-slot:item.ix="{ item }">
          {{ ownplayers.indexOf(item) + 1 }} 
        </template>
      </v-data-table>
    </div>
    <div class="mt-2">
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
      nmheaders: [
        { text: '#', value: 'ix', sortable: false },
        { text: this.$t("First name"), value: "first_name", sortable: true },
        { text: this.$t("Last name"), value: "last_name", sortable: true },
        { text: this.$t("ID number"), value: "idnumber", sortable: false },
        { text: "Club ID", value: "idclub", sortable: true },
        { text: "Nat. Elo", value: "natrating", sortable: true },
        { text: "Fide Elo", value: "fiderating", sortable: true },
        { text: 'Actions', value: 'actions', sortable: false },
      ],
      plheaders: [
        { text: '#', value: 'ix', sortable: false },
        { text: this.$t("First name"), value: "first_name", sortable: true },
        { text: this.$t("Last name"), value: "last_name", sortable: true },
        { text: this.$t("ID number"), value: "idnumber", sortable: false },
        { text: "Club ID", value: "idclub", sortable: true },
        { text: "Nat. Elo", value: "natrating", sortable: true },
        { text: "Fide Elo", value: "fiderating", sortable: true },
        { text: 'Actions', value: 'actions', sortable: false },
      ],
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
    activemembers() {
      return this.$store.state.playerlist.activemembers
    },
    newmembers() {
      const pl = new Set()
      this.players.forEach((x) => pl.add(x.idnumber))
      return this.activemembers.filter(x => !pl.has(x.idnumber))
    },
    players() {
      return this.$store.state.playerlist.players
    },
    ownplayers() {
      return this.players.filter(x => !x.transfer)
    },
    transfersin() {
      return this.players.filter(x => x.transfer)
    },
    transfersout() {
      return this.$store.state.playerlist.transfersout
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
      this.$store.commit('playerlist/updatePlayers', players)
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
      this.$store.commit('playerlist/updateStep', this.step + 1)
    },

    prev() {
      this.$store.commit('playerlist/updateStep', this.step - 1)
    },

    removeMember(p) {
      const players = [... this.players]
      const ix = players.indexOf(p)
      players.splice(ix, 1)
      this.$store.commit('playerlist/updatePlayers', players)
    },

  }
}
</script>


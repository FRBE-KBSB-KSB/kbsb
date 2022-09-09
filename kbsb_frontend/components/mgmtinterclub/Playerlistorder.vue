<template>
  <div>
    <h3>{{ $t('Order of players') }}</h3>
    <div>{{ $t('Order the players by adjusting the assigned rating.') }}</div>
    <div>{{ $t('Players with the same assigned rating are not allowed.') }}</div>
    <p>{{ $t('Click on the value of assigned rating to change it')}}</p>
    <v-data-table :items="plyrs" :headers="arheaders">
      <template v-slot:item.assignedrating="props">
        <v-edit-dialog :return-value="props.item.assignedrating" large :save-text="$t('Save')"
          :cancel-text="$t('Cancel')" @save="save(props.item)">
          {{ props.item.assignedrating }}
          <template v-slot:input>
            <v-text-field v-model="props.item.assignedrating" label="Edit" single-line>
            </v-text-field>
          </template>
        </v-edit-dialog>
      </template>
    </v-data-table>
    <v-alert type="warning" v-show="samerating">
      {{ $t('There are players with the same assigned rating.') }}
    </v-alert>
    <div class="mt-2">
      <v-btn color="green" class="white--text" @click="next" :disabled="samerating">
        {{ $t('Continue') }}
      </v-btn>
      <v-btn @click="prev">
        {{ $t('Back') }}
      </v-btn>
    </div>
  </div>
</template>

<script>

function compareAssignedrating(a, b) {
  return b.assignedrating - a.assignedrating
}

export default {

  data() {
    return {
      arheaders: [
        { text: "First name", value: "first_name", sortable: false },
        { text: "Last name", value: "last_name", sortable: false },
        { text: "ID number", value: "idnumber", sortable: false },
        { text: "Nat. Elo", value: "natrating", sortable: false },
        { text: "Fide Elo", value: "fiderating", sortable: false },
        { text: "Min", value: "minrating", sortable: false },
        { text: "Max", value: "maxrating", sortable: false },
        { text: "Assigned Rating", value: "assignedrating", sortable: false },
      ],
    }
  },

  computed: {
    players() {
      return this.$store.state.mgmtplayerlist.players
    },
    step() {
      return this.$store.state.mgmtplayerlist.step
    },
    samerating() {
      let prev = 3000
      return this.players.some((x) => {
        if (x.assignedrating == prev) return true
        prev = x.assignedrating
      })
    }
  },
  
  methods: {
    buildplayers() {
      console.log('buildplayers')
      const players = JSON.parse(JSON.stringify(this.players))
      players.forEach((x) => {
        let nr = x.natrating || 0
        let fr = x.fiderating || 0
        if (nr > 0 && fr > 0) {
          if (x.assignedrating == null) x.assignedrating = nr
          x.maxrating = Math.max(nr, fr) + 100
          x.minrating = Math.min(nr, fr) - 100
        }
        if (nr > 0 && fr == 0) {
          if (x.assignedrating == null) x.assignedrating = nr
          x.maxrating = nr + 100
          x.minrating = nr - 100
        }
        if (nr == 0 && fr > 0) {
          if (x.assignedrating == null) x.assignedrating = fr
          x.maxrating = fr + 100
          x.minrating = fr - 100
        }
        if (nr == 0 && fr == 0) {
          if (x.assignedrating == null) x.assignedrating = 1150
          x.maxrating = 1250
          x.minrating = 1050
        }
      })
      players.sort(compareAssignedrating)
      this.plyrs = players
    },

    next() {
      this.$store.commit('playerlist/updateStep', this.step + 1)
    },
    prev() {
      this.$store.commit('playerlist/updateStep', this.step - 1)
    },
    save(pl) {
      if (pl.minrating <= pl.assignedrating && pl.assignedrating <= pl.maxrating) {
        this.plyrs.sort(compareAssignedrating)
        this.$store.commit('playerlist/updatePlayers', this.plyrs)
        this.$forceUpdate()
      }
      else {
        this.$root.$emit('snackbar', { text: this.$t('Invalid value for assigned rating') })
      }
    },

  },

  mounted() {
    this.$root.$on('buildplayers', (ev) => {
      console.log('')
      this.buildplayers()
    })
  },


}
</script>


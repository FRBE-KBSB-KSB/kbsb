<template>
  <div>
    <h3>Order of players</h3>
    <div>Order the players by adjusting the assigned rating</div>
    <div>Players with the same assigned rating are not allowed.</div>
    <v-data-table sort-by.sync="assignedrating" :sort-desc="true" :items="players"
      :headers="arheaders" :must-sort="true">
      <template v-slot:item.assignedrating="props">
        <v-edit-dialog :return-value.sync="props.item.assignedrating" @save="save" @cancel="cancel"
          @open="open" @close="close">
          {{ props.item.assignedrating }}
          <template v-slot:input>
            <v-text-field v-model="props.item.assignedrating" label="Edit" single-line>
            </v-text-field>
          </template>
        </v-edit-dialog>
      </template>
    </v-data-table>
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
      arheaders: [
        { text: "First name", value: "first_name", sortable: false },
        { text: "Last name", value: "last_name", sortable: false },
        { text: "ID number", value: "idnumber", sortable: false },
        { text: "Nat. Elo", value: "natrating", sortable: false },
        { text: "Fide Elo", value: "fiderating", sortable: false },
        { text: "Assigned Rating", value: "fiderating", sortable: true },
        // { text: 'Actions', value: 'actions', sortable: false },
      ],
      snack: false,
      snackColor: '',
      snackText: '',
    }
  },

  computed: {
    players() {
      return this.$store.state.mgmtplayerlist.players
    },
    step() {
      return this.$store.state.mgmtplayerlist.step
    }
  },

  methods: {
    initAdjustedRating() {
      const players = [...this.players]
      players.forEach(x => {
        if (x.assignedrating == 0) {
          x.assignedrating = Math.max(x.natrating, x.fiderating)
        }
        if (x.assignedrating == 0) {
          x.assignededrating = 1000;
        }
      })
      this.$store.commit('mgmtplayerlist/updatePlayers', players)
    },

    next() {
      this.$store.commit('mgmtplayerlist/updateStep', this.step + 1)
    },
    prev() {
      this.$store.commit('mgmtplayerlist/updateStep', this.step - 1)
    },
    save() {
      console.log('saving assigned rating')
    },
    cancel() {
      console.log('canceling assigned rating')
    },
    open() {
      console.log('opening assigned rating')
    },
    close() {
      console.log('closing assigned rating')
    },
  },
  mounted() {
    this.initAdjustedRating();
  }
}
</script>


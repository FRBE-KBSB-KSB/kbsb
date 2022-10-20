<template>
  <v-container>
    <div v-for="m in matches" :key="m.id">
      <v-simple-table dense class="ma-3">
        <template v-slot:default>
          <thead>
            <tr>
              <th><b>{{ m.division}}{{m.series}}</b></th>
              <th>{{ m.club_home}}</th>
              <th>Total</th>
              <th>{{ m.club_visit}}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(b,ix) in m.boards" :key="ix">
              <td>{{ ix +1}}</td>
              <td>{{ b.playername_home}} ({{ b.playerrating_home }})</td>
              <td>{{ b.result }}</td>
              <td>{{ b.playername_visit}} ({{ b.playerrating_visit }})</td>
            </tr>
          </tbody>
        </template>

      </v-simple-table>
    </div>
  </v-container>
</template>
<script>

export default {

  name: 'Result',

  data() {
    return {
      division: 1,
      idclub: null,
      matches: [],
      round: 1,
      series: ''
    }
  },

  computed: {
    divseries: function () { return this.division + this.series }
  },

  mounted() {
    this.get_interclubmatches()
  },

  methods: {
    async get_interclubmatches() {
      console.log('fetching interclubmatches', this.$api)
      const options = {}
      if (this.idclub) { options.idclub = this.idclub; }
      if (this.round) { options.round = this.round; }
      if (this.divseries.length) { options.divseries = this.divseries; }
      try {
        const reply = await this.$api.interclub.get_interclubmatches(options)
        this.readMatches(reply.data.matches)
      }
      catch (error) {
        const reply = error.response
        console.error('getting matches', reply)
        this.$root.$emit('snackbar', { text: this.$t('Getting interclub matches failed') })
      }
    },

    readMatches(matches) {
      this.matches = matches
    }
  },

}
</script>

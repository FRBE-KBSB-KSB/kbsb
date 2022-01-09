<template>
  <v-container>
    <h1>{{ $t('Calender') }}</h1>
    <ul>
      <li v-for="c,ix in calitems" :key="ix">
        {{ calenderItem(c) }}
      </li>
    </ul>
  </v-container>
</template>

<script>
export default {

  data () {
    return {
      calitems: []
    }
  },
  async fetch () {
    const today = (new Date()).toISOString()
    const reply = await this.$content('calendar').fetch()
    this.calitems = reply.calendar
      .filter(c => c.datum > today)
      .sort((a, b) => a.datum > b.datum ? 1 : -1)
  },

  methods: {
    calenderItem (c) {
      const output = []
      output.push((new Date(c.datum)).toLocaleDateString(this.$i18n.locale, { dateStyle: 'medium' }) + ':')
      output.push(c.title)
      if (c.round) {
        output.push(this.$t('Round'))
        output.push(c.round)
      }
      return output.join(' ')
    }
  }

}
</script>

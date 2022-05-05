<template>
  <v-container>
    <h1>{{ $t('Calender') }}</h1>
    <ul>
      <li v-for="c,ix in future_ci" :key="ix">
        {{ calenderItem(c) }}
        <div v-if="!!c.text">
          {{ calendarText(c) }}
        </div>
        <div v-if="!!c.link">
          URL: <a :href="c.link">{{ c.link }}</a>
        </div>
        <br>
      </li>
    </ul>
  </v-container>
</template>

<script>

function compareDates (a, b) {
  return a.date - b.date
}
export default {

  data () {
    return {
      calitems: []
    }
  },

  async fetch () {
    const reply = await this.$content('calendar').fetch()
    this.calitems = []
    this.parseCalendarItems(reply)
    this.calitems.sort(compareDates)
  },

  computed: {
    future_ci () {
      const yesterday = new Date() - 86400000
      return this.calitems.filter(ci => ci.date > yesterday)
    }
  },

  methods: {

    calenderItem (c) {
      const output = []
      output.push(c.date.toLocaleDateString(this.$i18n.locale, { dateStyle: 'medium' }) + ':')
      output.push(c.title)
      if (c.round) {
        output.push(this.$t('Round'))
        output.push(c.round)
      }
      if (c.status === 'postponed') {
        output.push(this.$t('postponed'))
      }
      return output.join(' ')
    },
    calenderText (c) {
      return ''
    },
    parseCalendarItems (listci) {
      listci.forEach((ci) => {
        if (ci.multiple) {
          this.parseCalendarItems(ci.multiple)
        }
        if (ci.date) {
          const item = { ...ci, date: new Date(ci.date) }
          this.calitems.push(item)
          return
        }
        if (ci.rounds) {
          Object.entries(ci.rounds).forEach(([rnr, date]) => {
            const { rounds, ...item } = { ...ci, date: new Date(date), round: rnr }
            this.calitems.push(item)
          })
        }
      })
    }
  }

}
</script>

<style scoped>
.disabled {
  color: #bbb
}
.postponed {
  color: #bbb
}
</style>

<template>
  <v-container>
    <h1>{{ $t('Calender') }}</h1>
    <ul>
      <li v-for="c,ix in calitems" :key="ix" :class="{postponed: postponed(c), disabled: disabled(c)}">
        {{ calenderItem(c) }}
        <div v-if="!!c.text">
          {{ calendarText(c) }}
        </div>
        <div v-if="!!c.link">
          URL: <a :href="c.link">{{ c.link }}</a>
        </div>
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
    const reply = await this.$content('app', 'calendar').fetch()
    this.calitems = reply.calendar
      .filter(c => c.date > today)
      .sort((a, b) => a.date > b.date ? 1 : -1)
  },

  methods: {

    calenderItem (c) {
      const output = []
      output.push((new Date(c.date)).toLocaleDateString(this.$i18n.locale, { dateStyle: 'medium' }) + ':')
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
    disabled: c => c.status === 'disabled',
    postponed: c => c.status === 'postponed'
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

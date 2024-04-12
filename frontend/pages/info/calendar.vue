<script setup>
import { ref, computed } from 'vue'
import { VContainer } from 'vuetify/lib/components/index.mjs';
const { locale, setLocale, t } = useI18n()
const localePath = useLocalePath()

const calitems = ref([])
const { data: caldata } = await useAsyncData('calendar',
  () => queryContent('/calendar').find())

function compareDates(a, b) {
  return a.date - b.date
}

const future_ci = computed(() => {
  const yesterday = new Date() - 86400000
  return calitems.value.filter(ci => ci.date > yesterday)
})

function calenderItem(c) {
  const output = []
  output.push(c.date.toLocaleDateString(locale, { dateStyle: 'medium' }) + ':')
  output.push(c.title)
  if (c.round) {
    output.push(t('Round'))
    output.push(c.round)
  }
  if (c.status === 'postponed') {
    output.push(t('postponed'))
  }
  return output.join(' ')
}

function calenderText(c) {
  return ''
}

function parseCalendarItems(listci) {
  listci.forEach((ci) => {
    if (ci.multiple) {
      parseCalendarItems(ci.multiple)
      return
    }
    if (ci.date) {
      const item = { ...ci, date: new Date(ci.date) }
      calitems.value.push(item)
      return
    }
    if (ci.rounds) {
      Object.entries(ci.rounds).forEach(([rnr, date]) => {
        const { rounds, ...item } = { ...ci, date: new Date(date), round: rnr }
        calitems.value.push(item)
      })
    }
  })
}

onMounted(()=> {
  parseCalendarItems(caldata.value)
  calitems.value.sort(compareDates)
})


</script>

<template>
  <VContainer class="markdowncontent">
    <h1>{{ $t('Calendar') }}</h1>
    <ul>
      <li v-for="c, ix in future_ci" :key="ix" class="calenderitem">
        {{ calenderItem(c) }}
        <div v-if="!!c.text">
          {{ calendarText(c) }}
        </div>
        <div v-if="!!c.link">
          URL: <a :href="c.link">{{ c.link }}</a>
        </div>
      </li>
    </ul>
  </VContainer>
</template>

<style scoped>
.disabled {
  color: #bbb
}

.postponed {
  color: #bbb
}

.calenderitem {
  margin: 8px 0;
}
</style>

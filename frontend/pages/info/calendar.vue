<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { parse } from 'yaml'
const { t, locale } = useI18n()

const { $backend } = useNuxtApp()
const calitems = ref([])
const caldata = ref([])
const yesterday = new Date() - 86400000

function addItem(ci) {
  console.log('add item', ci.date, yesterday)
  if (ci.date > yesterday) {
    calitems.value.push(ci)
  }
}

function calenderItem(c) {
  const output = []
  output.push(c.date.toLocaleDateString(locale.value, { dateStyle: 'medium' }) + ':')
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

async function getCalendar(cal) {
  try {
    const reply = await $backend('filestore', 'anon_get_file', {
      group: 'calendar',
      name: cal.name,
    })
    cal.data = await parseYaml(reply.data)
    console.log("yaml processed", cal.name, cal.data)
  }
  catch (error) {
    console.error(' get calendar failed', error)
  }
}

async function getCalendarList() {
  try {
    const reply = await $backend('filestore', 'anon_get_filelist', {
      group: 'calendar',
    })
    await readCalenders(reply.data)
  }
  catch (error) {
    console.error('get calendarlist failed', error)
  }
}

async function parseYaml(yamlcontent) {
  try {
    return parse(yamlcontent)
  }
  catch (error) {
    console.error('cannot parse yaml', yamlcontent)
  }
}

function processCalendar(ci) {
  if (ci.multiple) {
    ci.multiple.forEach((c) => processCalendar(c))
  }
  if (ci.date) {
    const item = { ...ci, date: new Date(ci.date) }
    addItem(item)
    return
  }
  if (ci.rounds) {
    Object.entries(ci.rounds).forEach(([rnr, date]) => {
      const { rounds, ...item } = { ...ci, date: new Date(date), round: rnr }
      addItem(item)
    })
  }
}

function processCalendars() {
  calitems.value = []
  caldata.value.forEach((cal) => {
    processCalendar(cal.data)
  })
  calitems.value.sort((a, b) => a.date > b.date)
}

async function readCalenders(lc) {
  caldata.value = []
  let allpromises = []
  lc.forEach(e => {
    let name = e.split('/')[1]
    if (name) {
      console.log('adding calendar', name)
      caldata.value.push({ name })
    }
  });
  caldata.value.forEach(async cal => {
    allpromises.push(getCalendar(cal))
  })
  await Promise.all(allpromises)
  processCalendars()
}

function updateLocale(l) {
  console.log('updating locale', l)
  if (process.client) {
    localStorage.setItem("locale", l)
  }
  locale.value = l
  processCalendars()
}

watch(locale, (nl, ol) => updateLocale(nl))

onMounted(() => {
  getCalendarList()
})

</script>

<template>
  <v-container>
    <h1>{{ t('Calendar') }}</h1>
    <ul>
      <li v-for="c, ix in calitems" :key="ix" class="calenderitem">
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

<style scoped>
.v-card-title {
  white-space: normal;
}

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
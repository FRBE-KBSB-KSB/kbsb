<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const config = useRuntimeConfig()
const { t, locale } = useI18n()
const { $backend } = useNuxtApp()

// data model
const reports_bm = ref(null)
const reports_ga = ref(null)
const tab = ref(0)

async function getReportsBm() {
  try {
    const resp = await $backend("filestore", "anon_get_filelist",
      { group: "reports_bm" })
    process_reports_bm(resp.data)
  } catch (error) {
    console.error('getting getFiles', error)
  }
}

async function getReportsGa() {
  try {
    const resp = await $backend("filestore", "anon_get_filelist",
      { group: "reports_ga" })
    process_reports_ga(resp.data)
  } catch (error) {
    console.error('getting getFiles', error)
  }
}

async function process_reports_bm(lr) {
  reports_bm.value = []
  let ix = 0
  lr.forEach((f) => {
    let name = f.split('/')[1]
    let named = name
    if (named.substr(0, 3) == "CA_") {
      named = named.substr(3)
    }
    let year = parseInt(named.substring(0, 4))
    let month = parseInt(named.substring(4, 6))
    let day = parseInt(named.substring(6, 8))
    try {
      let d = new Date(year, month - 1, day, 12)
      reports_bm.value.push({
        name,
        topicdate: d,
        topicdatestr: date2iso(d),
        url: url_bm(name)
      })
    }
    catch (RangeError) {
      console.log('Could not read date from', name)
    }
  })
  reports_bm.value.sort((a, b) => { return a.topicdate.getTime() < b.topicdate.getTime() })
}

async function process_reports_ga(lr) {
  reports_ga.value = []
  let ix = 0
  lr.forEach((f) => {
    let name = f.split('/')[1]
    let named = name
    if (named.substr(0, 3) == "AG_") {
      named = named.substr(3)
    }
    let year = parseInt(named.substring(0, 4))
    let month = parseInt(named.substring(4, 6))
    let day = parseInt(named.substring(6, 8))
    try {
      let d = new Date(year, month - 1, day, 12)
      reports_ga.value.push({
        name,
        topicdate: d,
        topicdatestr: date2iso(d),
        url: url_ga(name)
      })
    }
    catch (RangeError) {
      console.log('Could not read date from', name)
    }
  })
  reports_ga.value.sort((a, b) => { return a.topicdate.getTime() < b.topicdate.getTime() })
}


function url_bm(name) {
  return "https://storage.cloud.google.com/website-kbsb-prod.appspot.com/reports_bm/" + name
}

function url_ga(name) {
  return "https://storage.cloud.google.com/website-kbsb-prod.appspot.com/reports_ga/" + name
}



onMounted(() => {
  getReportsBm();
  getReportsGa();
})

</script>

<template>
  <v-container>
    <h1>{{ $t('Reports') }}</h1>
    <v-tabs v-model="tab" light slider-color="deep-purple">
      <v-tab class="mx-2">{{ t('Report Board Meeting') }} </v-tab>
      <v-tab class="mx-2">{{ t('Report General Assembly') }} </v-tab>
    </v-tabs>
    <v-window v-model="tab">
      <v-window-item>
        <h3>{{ t('Report Board Meeting') }}</h3>
        <v-list>
          <v-list-item v-for="r in reports_bm">
            {{ r.topicdatestr }}:
            <a :href="r.url" target="report">
              {{ r.name }}
            </a>
          </v-list-item>
        </v-list>
      </v-window-item>
      <v-window-item>
        <h3>{{ t('Report General Assembly') }}</h3>
        <v-list>
          <v-list-item v-for="r in reports_ga">
            {{ r.topicdatestr }}:
            <a :href="r.url" target="report">
              {{ r.name }}
            </a>
          </v-list-item>
        </v-list>
      </v-window-item>
    </v-window>
  </v-container>
</template>

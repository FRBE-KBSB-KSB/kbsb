<script setup>
import { ref } from "vue"
import { useI18n } from "vue-i18n"

// communication
defineExpose({ setup })
const { t } = useI18n()
const { $backend } = useNuxtApp()

// snackbar and laoding weidgets
import ProgressLoading from "@/components/ProgressLoading.vue"
import SnackbarMessage from "@/components/SnackbarMessage.vue"
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

// data model
const icclub = ref({})
const ic_director = ref({})
let idclub = 0
const cnt_status = ref("noclub")

// methods alphabetically

async function getClubInterclubData() {
  let reply
  console.log("getting club interclub data for", idclub)
  if (!idclub) {
    cnt_status.value = "noclub"
    return
  }
  cnt_status.value = "open"
  showLoading(true)
  try {
    reply = await $backend("club", "anon_get_club", {
      idclub,
    })
  } catch (error) {
    displaySnackbar(t(t(error.message)))
    return
  } finally {
    showLoading(false)
  }
  icclub.value = reply.data
  ic_director.value = icclub.value.boardmembers.interclub_director
}

async function setup(idclub_) {
  console.log("setup contact", idclub_)
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  idclub = idclub_
  await getClubInterclubData()
}
</script>
<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <v-alert
      type="warning"
      variant="outlined"
      v-if="cnt_status == 'noclub'"
      :text="t('icn.select_club')"
    />
    <div v-if="cnt_status == 'open'">
      <h3>{{ $t("Contact") }} {{ $t("Interclubs") }}</h3>
      <v-card class="elevation-5">
        <v-card-title>{{ $t("Contact details") }}</v-card-title>
        <v-card-text>
          <div>
            <b>{{ $t("Email address Interclub") }}:</b>
            {{ icclub.email_interclub }}
          </div>
          <div class="mt-3">
            <b>{{ $t("interclub_director") }}:</b>
            {{ ic_director.last_name }}, {{ ic_director.first_name }}
          </div>
          <div>
            <b>{{ $t("Email") }}</b>
            {{ ic_director.email }}
          </div>
          <div>
            <b>{{ $t("Mobile") }}</b>
            {{ ic_director.mobile }}
          </div>
        </v-card-text>
      </v-card>
    </div>
  </v-container>
</template>

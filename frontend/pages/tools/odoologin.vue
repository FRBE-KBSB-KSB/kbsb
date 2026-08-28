<script setup>
import { ref } from "vue"
import { useI18n } from "vue-i18n"
import { useIdtokenStore } from "@/store/idtoken"
import { useIdnumberStore } from "@/store/idnumber"

const { locale, t } = useI18n()
const { $backend } = useNuxtApp()
const router = useRouter()
const route = useRoute()
const idstore = useIdtokenStore()
const idnstore = useIdnumberStore()

const login = ref({})
const snackbar = ref(null)
const errortext = ref("")
const url = route.query.url

function gotoOdoo(i) {
  console.log("gotoOdoo", i)
  if (i === 1) {
    let odooUrl = "https://frbe-kbsb.odoo.com/web/reset_password"
    window.open(odooUrl, "_blank")
    return
  }
  let odooUrl = "https://frbe-kbsb.odoo.com/"
  window.open(odooUrl, "_blank")
}

async function dologin() {
  console.log("doing a login")
  const returnUrl = url ? url.replaceAll("__", "/") : "/"
  console.log("return URL", returnUrl)
  let reply
  try {
    reply = await $backend("member", "login", {
      idnumber: login.value.idnumber,
      password: login.value.password,
    })
    console.log("did a login", reply.data)
  } catch (error) {
    console.error("failed login", error)
    errortext.value = t(error.message)
    snackbar.value = true
    return
  } finally {
    console.log("reached finally")
  }
  idstore.updateToken(reply.data)
  idnstore.updateIdnumber(login.value.idnumber)
  console.log("redirecting to ", returnUrl)
  await navigateTo(returnUrl)
  // router.push(returnUrl)
  console.log("navigated")
}

definePageMeta({
  layout: "nomenu",
})
</script>
<template>
  <VContainer>
    <VRow align="start">
      <VCol cols="12" md="8" offset-md="2" lg="8" offset-lg="2">
        <VCard>
          <VCardTitle>
            <VIcon large> mdi-account </VIcon>
            <label class="headline ml-3">{{ $t("Sign in") }}</label>
          </VCardTitle>
          <VDivider />
          <VCardText>
            <p>{{ $t("odoo.login") }}</p>
            <VTextField v-model="login.idnumber" :label="$t('Email address')" />
            <VTextField
              v-model="login.password"
              xs="12"
              lg="6"
              :label="$t('Password')"
              type="password"
            />
          </VCardText>
          <VCardActions>
            <VSpacer />
            <a @click="gotoOdoo(1)">
              {{ $t("odoo.lostpassword") }}
            </a>
            <a @click="gotoOdoo(2)">
              {{ $t("odoo.noaccount") }}
            </a>
            <VBtn @click="dologin()">
              {{ $t("Submit") }}
            </VBtn>
          </VCardActions>
        </VCard>
      </VCol>
    </VRow>
    <VSnackbar v-model="snackbar" timeout="6000">
      {{ errortext }}
      <template v-slot:actions>
        <v-btn
          color="green-lighten-2"
          variant="text"
          @click="snackbar = false"
          icon="mdi-close"
        />
      </template>
    </VSnackbar>
  </VContainer>
</template>

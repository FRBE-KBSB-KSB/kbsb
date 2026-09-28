<script setup>
import { ref } from "vue"
import { useI18n } from "vue-i18n"
import { useIdtokenStore } from "@/store/idtoken"
import { useIdbelStore } from "~/store/idbel"

const { locale, t } = useI18n()
const { $backend } = useNuxtApp()
const router = useRouter()
const route = useRoute()
const idtokenstore = useIdtokenStore()
const idbelstore = useIdbelStore()

const login = ref({})
const snackbar = ref(null)
const errortext = ref("")
const url = route.query.url

function gotoOdoo(i) {
  if (i === 1) {
    let odooUrl = "https://frbe-kbsb.odoo.com/web/reset_password"
    window.open(odooUrl, "_blank")
    return
  }
  let odooUrl = "https://frbe-kbsb.odoo.com/"
  window.open(odooUrl, "_blank")
}

async function dologin() {
  const returnUrl = url ? url.replaceAll("__", "/") : "/"
  let reply
  try {
    reply = await $backend("accounts", "odoologin", {
      email: login.value.email,
      password: login.value.password,
    })
  } catch (error) {
    console.error("failed login", error?.message)
    errortext.value = t(error.message)
    snackbar.value = true
    return
  }
  idbelstore.updateIdbel(reply.data[0])
  idtokenstore.updateToken(reply.data[1])
  await navigateTo(returnUrl)
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
          <form id="odoo-login-form" @submit.prevent="dologin()">
          <VCardText>
            <p>{{ $t("odoo.login") }}</p>
            <VTextField
              v-model="login.email"
              :label="$t('Email address')"
              name="username"
              type="email"
              autocomplete="username"
            />
            <VTextField
              v-model="login.password"
              xs="12"
              lg="6"
              :label="$t('Password')"
              name="password"
              type="password"
              autocomplete="current-password"
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
            <VBtn type="submit">
              {{ $t("Submit") }}
            </VBtn>
          </VCardActions>
          </form>
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

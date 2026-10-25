<script setup>
import { ref } from "vue"
import { useI18n } from "vue-i18n"
import { useIdtokenStore } from "@/store/idtoken"
import { useIdbelStore } from "~/store/idbel"
import ProgressLoading from "@/components/ProgressLoading.vue"
import SnackbarMessage from "@/components/SnackbarMessage.vue"

const { locale, t } = useI18n()
const { $backend } = useNuxtApp()
const router = useRouter()
const route = useRoute()
const idtokenstore = useIdtokenStore()
const idbelstore = useIdbelStore()

//  snackbar and loading widgets
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

const login = ref({})
const returnUrl = route.query.url ? route.query.url.replaceAll("__", "/") : "/"

const dialog2fa = ref(false)
const totpCode = ref("")

function gotoOdoo(i) {
  if (i === 1) {
    let odooUrl = "https://frbe-kbsb.odoo.com/web/reset_password"
    window.open(odooUrl, "_odoo")
    return
  }
  let odooUrl = "https://frbe-kbsb.odoo.com/"
  window.open(odooUrl, "_odoo")
}

async function dologin() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("accounts", "odoologin", {
      email: login.value.email,
      password: login.value.password,
    })
  } catch (error) {
    console.error("failed login", error?.message)
    showSnackbar(error?.message)
    return
  } finally {
    showLoading(false)
  }
  let loginreply = reply.data
  console.log("reply from login", loginreply)
  if (loginreply.is2FAneeded) {
    dialog2fa.value = true
  } else {
    idtokenstore.updateToken(loginreply.jwttoken)
    // TODO check if idbel is needed
    // (getting it via the standard APIkey interface of Odoo)
    await navigateTo(returnUrl)
  }
}

async function dologin2FA() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("accounts", "odoologin", {
      email: login.value.email,
      password: login.value.password,
    })
  } catch (error) {
    console.error("failed login", error?.message)
    showSnackbar(error.message)
    return
  } finally {
    showLoading(false)
  }
  let loginreply = reply.data
  console.log("reply from login", loginreply)
  if (loginreply.is2FAneeded) {
    dialog2fa.value = true
  } else {
    idtokenstore.updateToken(loginreply.jwttoken)
    // TODO check if idbel is needed
    // (getting it via the standard APIkey interface of Odoo)
    await navigateTo(returnUrl)
  }
}

definePageMeta({
  layout: "nomenu",
})

onMounted(() => {
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
})
</script>
<template>
  <VContainer>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <VRow align="start">
      <VCol cols="12" md="8" offset-md="2" lg="8" offset-lg="2">
        <VCard>
          <VCardTitle>
            <VIcon large> mdi-account </VIcon>
            <label class="headline ml-3">{{ $t("Sign in") }}</label>
          </VCardTitle>
          <VDivider />
          <form id="odoo-login-form" novalidate @submit.prevent="dologin()">
            <VCardText>
              <p>{{ $t("odoo.login") }}</p>
              <VTextField
                v-model="login.email"
                :label="$t('Email address')"
                name="username"
                type="text"
                inputmode="email"
                autocapitalize="off"
                spellcheck="false"
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
    <VDialog v-model="dialog2fa" max-width="450">
      <VCard>
        <VCardTitle>
          <VIcon large> mdi-shield-key-outline </VIcon>
          <label class="headline ml-3">{{ $t("odoo.2fa_title") }}</label>
        </VCardTitle>
        <VDivider />
        <form id="odoo-2fa-form" novalidate @submit.prevent="dologin2FA()">
          <VCardText>
            <p class="mb-4">{{ $t("odoo.2fa_prompt") }}</p>
            <VTextField
              v-model="totpCode"
              :label="$t('odoo.2fa_code')"
              name="totp"
              type="text"
              inputmode="numeric"
              autocomplete="one-time-code"
              maxlength="6"
              autofocus
            />
          </VCardText>
          <VCardActions>
            <VSpacer />
            <VBtn variant="text" @click="dialog2fa = false">
              {{ $t("Cancel") }}
            </VBtn>
            <VBtn type="submit" :disabled="!totpCode">
              {{ $t("Submit") }}
            </VBtn>
          </VCardActions>
        </form>
      </VCard>
    </VDialog>
  </VContainer>
</template>
<style scoped>
a {
  cursor: pointer;
}
</style>

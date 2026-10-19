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

const dialog2fa = ref(false)
const totpCode = ref("")
const dialogError = ref("")
const loading = ref(false)

function gotoOdoo(i) {
  if (i === 1) {
    let odooUrl = "https://frbe-kbsb.odoo.com/web/reset_password"
    window.open(odooUrl, "_blank")
    return
  }
  let odooUrl = "https://frbe-kbsb.odoo.com/"
  window.open(odooUrl, "_blank")
}

function open2faDialog() {
  dialogError.value = ""
  dialog2fa.value = true
}

function close2faDialog() {
  dialog2fa.value = false
  totpCode.value = ""
  dialogError.value = ""
}

async function submit2fa() {
  await dologin(true)
}

async function dologin(withTotp = false) {
  const returnUrl = url ? url.replaceAll("__", "/") : "/"
  loading.value = true
  dialogError.value = ""
  let reply
  try {
    const payload = {
      email: login.value.email,
      password: login.value.password,
    }
    const cleanTotp = totpCode.value ? totpCode.value.replace(/\s+/g, "") : ""
    if (cleanTotp) {
      payload.totp = cleanTotp
      payload.code = cleanTotp
    }
    reply = await $backend("accounts", "odoologin", payload)
  } catch (error) {
    loading.value = false
    console.error("failed login", error?.message)
    const detail = String(error?.response?.data?.detail || error?.message || "")
    if (
      !withTotp &&
      (detail.toLowerCase().includes("2fa") ||
        detail.toLowerCase().includes("totp") ||
        error?.response?.data?.requires_2fa ||
        error?.response?.data?.totp_required)
    ) {
      open2faDialog()
      return
    }
    const message = t(error.message)
    if (dialog2fa.value) {
      dialogError.value = message
    } else {
      errortext.value = message
      snackbar.value = true
    }
    return
  } finally {
    loading.value = false
  }
  dialog2fa.value = false
  totpCode.value = ""
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
            <a @click="open2faDialog()">
              {{ $t("odoo.2fa_link") }}
            </a>
            <VBtn type="submit" :loading="loading" :disabled="loading">
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
        <form id="odoo-2fa-form" novalidate @submit.prevent="submit2fa()">
          <VCardText>
            <VAlert
              v-if="dialogError"
              type="error"
              density="compact"
              class="mb-3"
            >
              {{ dialogError }}
            </VAlert>
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
            <VBtn variant="text" @click="close2faDialog()">
              {{ $t("Cancel") }}
            </VBtn>
            <VBtn type="submit" :loading="loading" :disabled="loading || !totpCode">
              {{ $t("Submit") }}
            </VBtn>
          </VCardActions>
        </form>
      </VCard>
    </VDialog>
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
<style scoped>
a {
  cursor: pointer;
}
</style>

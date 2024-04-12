<script setup>
import { ref, computed, onMounted } from 'vue'
import { VContainer, VBtn, VCard, VCardTitle, VCardText, VCardActions, VRow, VIcon, VTextField, 
  VCol, VDivider, VDialog, VSnackbar, VSpacer } from 'vuetify/lib/components/index.mjs';
import { useRouter, useRoute } from 'vue-router'
import { useIdtokenStore}  from '@/store/idtoken'
import { useIdnumberStore}  from '@/store/idnumber'
import showdown from 'showdown'

const { locale, t } = useI18n()
const localePath = useLocalePath()
const { $backend } = useNuxtApp()
const router = useRouter() 
const route = useRoute()
const idstore = useIdtokenStore()
const idnstore = useIdnumberStore()

// help dialog 
const ttitle = `title_${locale.value}`
const tcontent = `content_${locale.value}`
const { data: help }  = await useAsyncData('help-login', () => queryContent('/pages/help-login').findOne())
const helpdialog = ref(false)
const login = ref({})
const snackbar = ref(null)
const errortext = ref("")
const url = route.query.url
const mdConverter = new showdown.Converter()
function md(s) { return  mdConverter.makeHtml(s)}

async function dologin() {
  const returnUrl = url ? url.replaceAll("__", "/") : '/'
  let reply
  try {
    reply = await $backend("member", "login", {
      idnumber: login.value.idnumber,
      password: login.value.password
    })
  } 
  catch(error) {
    errortext.value = t(error.message)
    snackbar.value = true
    return
  }
  idstore.updateToken(reply.data)
  idnstore.updateIdnumber(login.value.idnumber)
  navigateTo(localePath(returnUrl))
}

</script>
<template>
  <VContainer>
    <VRow align="start">
      <VCol cols="12" md="6" offset-md="3" lg="6" offset-lg="3">
        <VCard>
          <VCardTitle>
            <VIcon large>
              mdi-account
            </VIcon>
            <label class="headline ml-3">{{ $t('Sign in') }}</label>
            <VBtn icon="mdi-help" color="green" class="float-right" @click="helpdialog = true" />           
          </VCardTitle>
          <VDivider />
          <VCardText>
            <VTextField v-model="login.idnumber" :label="$t('ID number')" />
            <VTextField v-model="login.password" xs="12" lg="6" :label="$t('Password')" type="password" />
          </VCardText>
          <VCardActions>
            <VSpacer />
            <VBtn @click="dologin()">
              {{ $t('Submit') }}
            </VBtn>
          </VCardActions>
        </VCard>
      </VCol>
    </VRow>
    <VDialog v-model="helpdialog" width="20em">
      <ContentRenderer :value="help">
        <VCard>
          <VCardTitle v-html="help[ttitle] ? help[ttitle] : help.title" />
          <VDivider />
          <VCardText class="pa-3 ma-1 markdowncontent" v-html="md(help[tcontent])" /> 
        </VCard>
      </ContentRenderer>
    </VDialog>
    <VSnackbar v-model="snackbar" timeout="6000">
      {{ errortext }}
      <template v-slot:actions>
        <v-btn color="green-lighten-2" variant="text" @click="snackbar = false" icon="mdi-close" />
      </template>
    </VSnackbar>     
  </VContainer>
</template>



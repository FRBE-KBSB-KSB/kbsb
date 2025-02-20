<script setup>
import { ref, onMounted } from "vue"
import * as jose from "jose"
import { usePersonStore } from "@/store/person"
import { storeToRefs } from "pinia"
import { useOneTap } from "vue3-google-signin"

// stores
const personstore = usePersonStore()
const { person } = storeToRefs(personstore)

// model
const authenticated = ref(false)

// google one tap
useOneTap({
  onSuccess: (resp) => {
    console.log("Success:", resp)
    const payload = jose.decodeJwt(resp.credential)
    personstore.updatePerson({
      credentials: resp.credential,
      user: payload.name,
      email: payload.email,
    })
    authenticated.value = true
  },
  onError: () => console.error("Error with One Tap Login"),
})

useHead({
  title: "Management Login",
})

definePageMeta({
  layout: "mgmt",
})
</script>

<template>
  <v-container class="markdowncontent">
    <h1>Management FRBE-KBSB-KSB</h1>
    <div v-if="!authenticated">
      <p>Waiting for authorization</p>
    </div>
    <ul v-if="authenticated">
      <li>Admin part <NuxtLink to="/mgmt/clubs">Clubs Manager</NuxtLink></li>
      <li>Admin part <NuxtLink to="/mgmt/interclubs">Interclubs Manager</NuxtLink></li>
      <li>
        Getting the <NuxtLink to="/mgmt/mailing">Mailing Lists</NuxtLink> for all clubs
      </li>
      <li>
        <NuxtLink to="/mgmt/logout">Logout</NuxtLink>
      </li>
    </ul>
  </v-container>
</template>

<script setup>
import { onMounted } from "vue"
import { usePersonStore } from "@/store/person"
import { storeToRefs } from "pinia"

const router = useRouter()
const personstore = usePersonStore()
const { person } = storeToRefs(personstore)

definePageMeta({
  layout: "mgmt",
})

useHead({
  title: "Management Overview",
})

function checkAuth() {
  if (person.value.credentials.length === 0) {
    router.push("/mgmt")
  }
  if (!person.value.email.endsWith("@frbe-kbsb-ksb.be")) {
    router.push("/mgmt")
  }
}

onMounted(() => {
  checkAuth()
})
</script>

<template>
  <v-container class="markdowncontent">
    <h1>Overview</h1>
    <ul>
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

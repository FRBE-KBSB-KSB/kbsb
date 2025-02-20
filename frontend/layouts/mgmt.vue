<script setup>
import { ref } from "vue"

const router = useRouter()
const drawer = ref(false)

async function goto(section) {
  const url = `/mgmt/${section}`
  router.push(url)
}

useHead({
  script: [{ src: "https://accounts.google.com/gsi/client", defer: true }],
})
</script>

<template>
  <VApp>
    <VNavigationDrawer v-model="drawer" class="bg-deep-purple-darken-1 text-white">
      <VToolbar class="bg-deep-purple-lighten-1 text-white">
        <VToolbarTitle>Menu</VToolbarTitle>
      </VToolbar>
      <VList class="bg-deep-purple-lighten-1 text-white">
        <VListItem @click="goto('')" title="Overview" />
        <VListItem @click="goto('clubs')" title="Clubs" />
        <VListItem @click="goto('interclubs')" title="Interclubs" />
        <VListItem @click="goto('mailing')" title="Mailing" />
        <VListItem @click="goto('logout')" title="Logout" />
      </VList>
    </VNavigationDrawer>
    <VAppBar class="bg-deep-purple-darken-1 text-white">
      <VAppBarNavIcon @click="drawer = !drawer" />
      <VAppBarTitle> Management FRBE- KBSB-KSB </VAppBarTitle>
    </VAppBar>
    <VMain>
      <slot />
    </VMain>
  </VApp>
</template>

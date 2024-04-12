<script setup>
import { ref } from "vue";
import {
  VApp, VAppBar, VAppBarTitle, VNavigationDrawer,
  VAppBarNavIcon, VMain, VList, VListItem, VToolbar, VToolbarTitle
} from 'vuetify/components'

const drawer = ref(false);

// we need ot because nuxt i18n is buggy
const localePath = useLocalePath()

async function goto(section) {
  const url = `/mgmt/${section}`
  console.log('going to', url)
  navigateTo(localePath(url))
}
</script>

<template>
  <VApp>
    <VNavigationDrawer v-model="drawer" class="bg-deep-purple-darken-1 text-white">
      <VToolbar class="bg-deep-purple-lighten-1 text-white">
        <VToolbarTitle>Menu</VToolbarTitle>
      </VToolbar>
      <VList class="bg-deep-purple-lighten-1 text-white">
        <VListItem @click="goto('overview')" title="Overview" />
        <VListItem @click="goto('content')" title="Site Content" />
        <VListItem @click="goto('clubs')" title="Clubs" />
        <VListItem @click="goto('filelist')" title="Files (Reports)" />
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

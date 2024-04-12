<script setup>
import { ref } from 'vue'
import TheSidebar from '@/components/TheSidebar.vue'
import TheCarousel from '@/components/TheCarousel.vue'
import TheFooter from '@/components/TheFooter.vue'
import { VApp, VAppBar, VAppBarTitle, VNavigationDrawer, 
  VAppBarNavIcon, VMain } from 'vuetify/components'

const drawer = ref(false)
</script>

<template>
  <div>
    <VApp>
      <v-navigation-drawer v-model="drawer" 
        class="bg-green-darken-1 text-white">
        <TheSidebar />
      </v-navigation-drawer>
      <v-app-bar color="green-darken-2">
        <v-app-bar-nav-icon @click="drawer = !drawer" />
        <v-app-bar-title>
          FRBE- KBSB-KSB
        </v-app-bar-title>
      </v-app-bar>
      <VMain>
        <slot />
        <TheCarousel /> 
        <hr />                 
      </VMain>
      <TheFooter />    
    </VApp>
  </div>
</template>


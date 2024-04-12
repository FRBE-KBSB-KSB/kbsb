<script setup>
import {ref} from 'vue'
import { VCarousel, VCarouselItem } from 'vuetify/lib/components/index.mjs';

const current = ref(0)
const interval = ref(6)
const items = ref([
  { src: '/img/frame_talistro.png', name: 'talistro' },
  { src: '/img/frame_ecu.png', name: 'ecu' },
  { src: '/img/frame_arena.png', name: 'arena' },
  { src: '/img/frame_boic.png', name: 'boic' },
  { src: '/img/frame_iheb.png', name: 'iheb' },
  { src: '/img/frame_fide.png', name: 'fide' }
])

onMounted(()=> {
  const secCarousel = Math.floor((new Date() / 1000) % (interval.vlue * items.value.length))
  current.value = Math.floor(secCarousel / items.value.length)
  if (current.value === items.value.length) {current.value = 0 }

})
</script>

<template>
  <v-carousel
    :show-arrows="false"
    hide-delimiters
    :value="current"
    height="170"
    class="adcarousel mb-2"
    :interval="interval*1000"
    cycle
    continuous
  >
    <v-carousel-item v-for="item in items" :key="item.name" :src="item.src" />
  </v-carousel>
</template>



<style scoped>
.adcarousel.v-carousel {
  width: 360px;
  max-width: 95%;
  margin-left: auto;
  margin-right: auto;
}
</style>

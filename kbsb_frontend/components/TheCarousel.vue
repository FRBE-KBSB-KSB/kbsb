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

<script>
export default {
  data () {
    return {
      current: 0,
      interval: 6, // number of seconds before switching
      items: [
        { src: '/img/frame_talistro.png', name: 'talistro' },
        { src: '/img/frame_ecu.png', name: 'ecu' },
        { src: '/img/frame_arena.png', name: 'arena' },
        { src: '/img/frame_boic.png', name: 'boic' },
        { src: '/img/frame_iheb.png', name: 'iheb' },
        { src: '/img/frame_fide.png', name: 'fide' }
      ]
    }
  },
  mounted () {
    const secCarousel = Math.floor((new Date() / 1000) % (this.interval * this.items.length))
    this.current = Math.floor(secCarousel / this.items.length)
    if (this.current === this.items.length) { this.current = 0 }
  }
}
</script>

<style scoped>
.adcarousel.v-carousel {
  width: 360px;
  max-width: 95%;
  margin-left: auto;
  margin-right: auto;
}
</style>

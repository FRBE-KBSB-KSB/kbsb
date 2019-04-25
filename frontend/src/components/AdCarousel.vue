<!--

   Copyright 2017 - 2018 Chessdevil Consulting BVBA

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

-->

<template>
<v-carousel hide-controls hide-delimiters :value="current" height="170"
            class="adcarousel mb-2" :interval="interval*1000">
  <v-carousel-item v-for="item in items" :key="item.name" :src="item.src">
  </v-carousel-item>
</v-carousel>

</template>

<script>
export default {
  data () {
    return {
      current: 0,
      interval: 5, // number of seconds before switching
      items: [
        {src: '/static/img/frame_talistro.png', name: 'talistro' },
        {src: '/static/img/frame_chessconsult.png', name: 'chessconsult' },
        {src: '/static/img/frame_matetmots.png', name: 'matetmots' },
        {src: '/static/img/frame_marchand.png', name: 'marchand' },
        {src: '/static/img/frame_chessdevil.png', name: 'chessdevil' },
      ]
    }
  },
  mounted () {
    var secCarousel = Math.floor((new Date()/1000) % (this.interval * this.items.length));
    this.current = Math.floor(secCarousel / this.items.length);
    if (this.current == this.items.length) this.current = 0;
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


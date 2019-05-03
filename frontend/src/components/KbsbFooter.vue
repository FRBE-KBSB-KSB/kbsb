<template>
<v-footer height="auto" color="green" dark class="mt-2">
  <v-container>
    <v-layout row wrap class="py-3">
      <v-flex sm4 xs12 class="mt-2">
        <h4 class="mb-2">
          {{ $t('Royal Belgian Chess Federation')}} {{ $t('npo')}}
        </h4>
        <div>{{ $t('Registered office')}}</div>
        <div>ALMA ECHECS, Jardin Martin V, 5<br>
           1200 Brussels   
        </div>
        <div>IBAN: BE76 0015 9823 0095</div>
        <div>BIC: GEBABEBB</div>
      </v-flex>
      <v-flex sm4 xs12 class="mt-2">
        <h4 class="mb-2">{{$t('Postal Address')}}</h4>
        <div>Opbrakelsestraat, 37<br>9660 Brakel</div>
      </v-flex>
      <v-flex sm4 xs12 class="mt-2">
        <h4 class="mb-2">Social media</h4>
        <div>e-mail: <a href="mailto:board@frbe-kbsb.be">board@frbe-kbsb.be</a></div>
        <div>
         Facebook: <a href="https://www.facebook.com/groups/1845828638985199/">
           <img style="vertical-align: middle" src="/static/img/facebook.png">
         </a>
        </div>
      </v-flex>
      <v-flex xs12 fluid class="text-xs-center green darken-2 mt-3 py-2 px-1">
        Website by <a target="_blank" href="https://www.chessdevil.net">
        Chessdevil Consulting</a>. &copy; 2018 - 2019.  All rights reserved
      </v-flex>
    </v-layout>
  </v-container>
</v-footer>
</template>

<script>
  export default {
    name: "KbsbFooter"
  }
</script>

<style scoped>

a {
 color: white;
}

a:link, a:hover {
  color: white;
  text-decoration: none;
}

a:hover {
  font-weight: 700;
}

</style>
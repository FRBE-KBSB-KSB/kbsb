<template>
<v-footer color="green" dark class="mt-2 footer" app absolute>
  <v-container fluid>
    <v-row class="py-3 px-2">
      <v-col cols="12" sm="4" class="mt-2">
        <h4 class="mb-2">
          {{ $t('Royal Belgian Chess Federation npo') }}
        </h4>
        <div>
          {{ $t('Registered office') }}
        </div>
        <div>
          131 Rue Frans Vekemansstraat 131<br>
          1120 Neder-Over-Heembeek
        </div>
        <div>IBAN: BE76 0015 9823 0095</div>
        <div>BIC: GEBABEBB</div>
      </v-col>
      <v-col cols="12" sm="4" class="mt-2">
        <h4 class="mb-2">
          {{ $t('Postal address') }}
        </h4>
        <div>14 boîte 1 Rue Jules Hans<br>1420 Braine-l'Alleud</div>
      </v-col>
      <v-col cols="12" sm="4" class="mt-2">
        <h4 class="mb-2">
          {{ $t("Social media") }}
        </h4>
        <div>e-mail: <a href="mailto:info@frbe-kbsb-ksb.be">info@frbe-kbsb-ksb.be</a></div>
        <div>
          <a href="https://www.facebook.com/groups/1845828638985199/">
            Facebook
          </a>
        </div>
      </v-col>
      <v-col cols="12" fluid class="d-flex justify-center green darken-2 mt-3 py-2 px-1">
        <span>
          Website by <a target="_blank" href="https://www.chessdevil.net">
            Chessdevil Consulting</a>. &copy; {{ new Date().getFullYear() }}.  All rights reserved
        </span>
      </v-col>
    </v-row>
  </v-container>
</v-footer>
</template>

<script>

export default {

  name: 'KbsbFooter'

}

</script>

<style scoped>

.footer a {
 color: white;
}

.footer a:link, .footer a:hover {
  color: white;
  text-decoration: none;
}

.footer a:hover {
  font-weight: 700;
}

</style>

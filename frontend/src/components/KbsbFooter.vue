<template>
<v-footer height="auto" color="green" dark class="mt-2">
  <v-container fluid>
    <v-row class="py-3 px-2">
      <v-col cols=12 sm=4 class="mt-2">
        <h4 class="mb-2">
          <i18n-text 
            nl="Koninklijke Belgische Schaakbond vzw."
            fr="Fédération Royale Balege des Echecs asbl."
            de="Königlicher Schachbund Belgien VoE"
            en="Royal Belgian Chess Federation npo"
          />
        </h4>
        <div>
          <i18n-text 
            nl="Maatschappelijke zetel"
            fr="Siège social"
            de="Sitz der Gesellschaft"
            en="Registered office"
          />
        </div>
        <div>
            ALMA ECHECS<br>
            Jardin Martin V, 59<br>
           1200 Brussel-Bruxelles   
        </div>
        <div>IBAN: BE76 0015 9823 0095</div>
        <div>BIC: GEBABEBB</div>
      </v-col>
      <v-col cols=12 sm=4 class="mt-2">
        <h4 class="mb-2">
          <i18n-text 
            nl="Postadres"
            fr="Adresse postale"
            de="Postanschrift"
            en="Postal address"
          />
        </h4>
        <div>14 boîte 1 Rue Jules Hans<br>1420 Braine-l'Alleud</div>
      </v-col>
      <v-col cols=12 sm=4 class="mt-2">
        <h4 class="mb-2">
          <i18n-text 
            nl="Sociale media"
            fr="Médias sociaux"
            de="Sozialen Medien"
            en="Social media"
          />
        </h4>
        <div>e-mail: <a href="mailto:info@frbe-kbsb-ksb.be">info@frbe-kbsb-ksb.be</a></div>
        <div>
         Facebook: <a href="https://www.facebook.com/groups/1845828638985199/">
           <img style="vertical-align: middle" src="@/assets/img/facebook.png">
         </a>
        </div>
      </v-col>
      <v-col cols=12 fluid class="d-flex justify-center green darken-2 mt-3 py-2 px-1">
        <span>
          Website by <a target="_blank" href="https://www.chessdevil.net">
          Chessdevil Consulting</a>. &copy; 2018 - 2020.  All rights reserved
        </span>
      </v-col>
    </v-row>
  </v-container>
</v-footer>
</template>

<script>

import I18nText from "@/components/I18nText"


export default {

  name: "KbsbFooter",

  components: {
    I18nText,
  }


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
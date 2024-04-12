<script setup>
import { VContainer, VRow, VCol } from 'vuetify/components';
</script>
<template>
  <v-container fluid class="bg-green-darken-2 text-white">
    <v-row class="py-3 px-2">
      <v-col cols="12" sm="4" class="mt-2">
        <h4>{{ $t('Address') }}</h4>
        <div>
          131 Rue Frans Vekemansstraat 131<br>
          1120 Neder-Over-Heembeek
        </div>
      </v-col>
      <v-col cols="12" sm="4" class="mt-2">
        <h4>{{ $t('Bank details') }}</h4>
        <div>IBAN: BE76 0015 9823 0095</div>
        <div>BIC: GEBABEBB</div>
      </v-col>
      <v-col cols="12" sm="4" class="mt-2">
        <h4>{{ $t('Contact') }}</h4>
        <div>e-mail: <a href="mailto:info@frbe-kbsb-ksb.be">info@frbe-kbsb-ksb.be</a></div>
        <div>
          <a href="https://www.facebook.com/groups/1845828638985199/">
            Facebook
          </a>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>
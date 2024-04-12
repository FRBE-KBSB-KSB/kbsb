<template>
  <v-container>
    <h1>Interclubs 2022-23: {{ $t('Dates') }}</h1>
    <ul>
      <li>18/09/2022 24h00: {{ $t('Closing time for modifying the playerlist') }}</li>
      <li>20/09/2022: {{ $t('Start entering planning') }}</li>
      <li>25/09/2022: {{ $t('Round') }} 1</li>
      <li>16/10/2022: {{ $t('Round') }} 2</li>
      <li>06/11/2022: {{ $t('Round') }} 3</li>
      <li>20/11/2022: {{ $t('Round') }} 4</li>
      <li>04/12/2022: {{ $t('Round') }} 5</li>
      <li>29/01/2022: {{ $t('Round') }} 6</li>
      <li>12/02/2023: {{ $t('Round') }} 7</li>
      <li>05/03/2023: {{ $t('Round') }} 8</li>
      <li>19/03/2023: {{ $t('Round') }} 9</li>
      <li>16/04/2023: {{ $t('Round') }} 10</li>
      <li>30/04/2023: {{ $t('Round') }} 11</li>
      <li>23/10/2022: Res. 1</li>
      <li>27/11/2022: Res. 2</li>
      <li>22/01/2023: Res. 3</li>
      <li>26/02/2023: Res. 4</li>
      <li>26/03/2023: Res. 5</li>
      <li>16/10/2022: Res. 6</li>
      <li>07/05/2023: Res. 7</li>
      <li>14/05/2023: Testmatch</li>
    </ul>

  </v-container>
</template>

<script>

import { marked } from 'marked'
import { notitle, nointro } from '@/util/cms'

export default {

  name: 'Enrollment',

  data() {
    return {
      ann: []
    }
  },

}
</script>
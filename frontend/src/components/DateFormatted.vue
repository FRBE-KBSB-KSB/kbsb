<template>
  <span>{{ dateformatted }}</span>
</template>

<script>
import * as moment from 'moment';

import 'moment/locale/en-gb'
import 'moment/locale/fr'
import 'moment/locale/nl';
import 'moment/locale/de'

moment.locale('en-gb');

export default {
  name: "DateFormatted",
  props: ["date", "fmt"],
  computed: {
    dateformatted () {
      return this.date ? moment(this.date).format(this.fmt ? this.fmt: 'lll'): '';
    }
  }
}
</script>

<style scoped>

</style>
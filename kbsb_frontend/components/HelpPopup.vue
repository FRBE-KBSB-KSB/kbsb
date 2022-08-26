<template>
  <v-dialog v-model="dialog" width="20em">
    <template v-slot:activator="{ on, attrs }">
      <v-btn color="green" fab outlined x-small v-bind="attrs" v-on="on">
        <v-icon>mdi-help</v-icon>
      </v-btn>
    </template>

    <v-card>
      <v-card-title>
        {{ content.title }}
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text class="pt-3" v-html="content.body">
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  data() {
    return {
      dialog: false,
      content: {},
    }
  },

  props: {
    file: String
  },

  methods: {
    async fetch() {
      this.content = (await this.$content('help', this.file).fetch())[this.$i18n.locale]
    },

  },

  mounted() {
    this.fetch()
  },
}
</script>
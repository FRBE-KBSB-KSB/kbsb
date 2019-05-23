<template>
<v-toolbar fixed dark dense app class="green darken-1">
  <v-toolbar-title>
    Administration
  </v-toolbar-title>
  <v-spacer></v-spacer>
  <v-toolbar-items>
    <v-btn flat large to="articles">Articles</v-btn>
  </v-toolbar-items>
  <v-toolbar-items>
    <v-btn flat large to="documents">Documents</v-btn>
  </v-toolbar-items>
  <v-toolbar-items>
    <v-btn flat large to="members">Members</v-btn>
  </v-toolbar-items>
</v-toolbar>
</template>

<script>
export default {
  name: "MgmtMenu",
}
</script>

<style scoped>
</style>
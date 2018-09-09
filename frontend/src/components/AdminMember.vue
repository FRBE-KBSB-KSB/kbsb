<template>
<div>

   <v-tabs v-model="tabix" class="mt-2" slider-color="green darken-2">
    <v-tab active-class="default-class green lighten-4">Members</v-tab>
    <v-tab active-class="default-class green lighten-4">Detail</v-tab>
    <v-tab active-class="default-class green lighten-4">Photo</v-tab>
  </v-tabs>

  <v-tabs-items v-model="tabix">
    <v-tab-item>
      <h3 class="mt-2">Attendee</h3>
      <admin-member-list></admin-member-list>
    </v-tab-item>
    <v-tab-item>
      <h3 class="mt-2">Detail</h3>
      <p>To DO</p>
    </v-tab-item>
    <v-tab-item>
      <h3 class="mt-2">Photo</h3>
      <p>To DO</p>
    </v-tab-item>
  </v-tabs-items>

</div>
</template>

<script>
export default {
  name: "AdminMember",
  data () {
    return {
      tabix: "0"
    }
  },
    
}
</script>

<style scoped>

</style>
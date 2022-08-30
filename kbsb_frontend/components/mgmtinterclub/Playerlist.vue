<template>
  <v-container>
    <p v-if="!club.idclub">Please select a club to edit the player list</p>
    <div v-if="club.idclub">
      <v-stepper v-model="step" vertical>

        <v-stepper-step :complete="step > 1" step="1" color="deep-purple">
          Intro
        </v-stepper-step>
        <v-stepper-content step="1">
          <MgmtinterclubPlayerlistintro />
        </v-stepper-content>

        <v-stepper-step :complete="step > 2" step="2" color="deep-purple">
          Define players
        </v-stepper-step>
        <v-stepper-content step="2">
          <MgmtinterclubPlayerlistplayers />
        </v-stepper-content>

        <v-stepper-step :complete="step > 3" step="3" color="deep-purple">
          Define order
        </v-stepper-step>
        <v-stepper-content step="3">
          <MgmtinterclubPlayerlistorder />
        </v-stepper-content>

        <v-stepper-step :complete="step > 4" step="4" color="deep-purple">
          Define teams
        </v-stepper-step>
        <v-stepper-content step="4">
          <MgmtinterclubPlayerlistteams />
        </v-stepper-content>

        <v-stepper-step :complete="step > 5" step="5" color="deep-purple">
          Confirm
        </v-stepper-step>
        <v-stepper-content step="5">
          <MgmtinterclubPlayerlistconfirm />
        </v-stepper-content>

      </v-stepper>
    </div>
  </v-container>
</template>
<script>
import Vue from 'vue'

export default {

  name: 'Enrollment',

  data() {
    return {
    }
  },

  props: {
    club: Object
  },

  computed: {
    step() {
      return this.$store.state.mgmtplayerlist.step
    }
  },

  methods: {

    emitInterface() {
      // this.$emit("interface", "find_interclubenrollment", this.find_interclubenrollment);
    },


  },

  mounted() {
    this.emitInterface();
  },

}
</script>
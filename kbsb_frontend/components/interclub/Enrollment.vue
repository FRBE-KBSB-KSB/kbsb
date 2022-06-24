<template>
  <v-container>
    <p v-if="!club.idclub">Please select a club to view the enrollment</p>
    <div v-if="club.idclub">
      <h3 v-show="status == 'consulting'">Existing Enrollment</h3>
      <h3 v-show="status == 'adding'">Add Enrollment</h3>
      <h3 v-show="status == 'modifying'">Modify Enrollment</h3>
      <div v-show="!enrollment.id && status == 'consulting'">
        <p>The club is not enrolled yet</p> 
        <v-btn @click="newEnrollment">
          New enrollment
        </v-btn>
      </div>
      <div v-show="enrollment.id && status == 'consulting'">
        <ul>
          <li>Teams in division 1: {{ enrollment.teams1 }}</li>
          <li>Teams in division 2: {{ enrollment.teams2 }}</li>
          <li>Teams in division 3: {{ enrollment.teams3 }} </li>
          <li>Teams in division 4: {{ enrollment.teams4 }} </li>
          <li>Teams in division 5: {{ enrollment.teams5 }}</li>
          </ul>
        <v-btn @click="modifyEnrollment">
          Modify enrollment
        </v-btn>
      </div>
      <div v-show="status == 'adding' || status == 'modifying'">
        <v-text-field v-model="enrollment.teams1" label="Teams in division 1" 
          type="number" min="0" max="15" />
        <v-text-field v-model="enrollment.teams2" label="Teams in division 2" 
          type="number" min="0" max="15" />
        <v-text-field v-model="enrollment.teams3" label="Teams in division 3" 
          type="number" min="0" max="15" />
        <v-text-field v-model="enrollment.teams4" label="Teams in division 4" 
          type="number" min="0" max="15" />
        <v-text-field v-model="enrollment.teams5" label="Teams in division 5" 
          type="number" min="0" max="15" />
        <v-btn @click="saveEnrollment">
          Save enrollment
        </v-btn>
      </div>
    </div>
  </v-container>
</template>
<script>
export default {

  name: 'Enrollment',

  data () {
    return {
      club: {},
      enrollment: {
        teams1: 0,
        teams2: 0,
        teams3: 0,
        teams4: 0,
        teams5: 0,
      },
      status: "consulting"
    }
  },



  computed: {
    logintoken () { return this.$store.state.oldlogin.value },
  },

  methods: {

    emitInterface(){
      this.$emit("interface", "enrollment", this.getAnonEnrollment);      
    },

    async getAnonEnrollment(activeclub){
      this.club = activeclub;
      console.log('running getAnonEnrollment')
      try {
        const reply = await this.$api.interclub.anon_get_enrollment({
          idclub: this.club.idclub
        })
        this.enrollment = reply.data
      } catch (error) {
        console.log('error', error)
        const reply = error.response
        console.error('getting anon_enrollment', reply)
        if (reply.status === 401) {
            this.gotoLogin()
        } 
        else {
          this.$root.$emit('snackbar', { text: 'Getting existing enrollment failed', reason: reply.data.detail })
        }
      }
    },

    async newEnrollment(){
      try {
        const reply = await this.$api.club.verify_club_access({
          token: this.logintoken,
          idclub: this.club.idclub,
          role: "InterclubAdmin"
        })
        const hasaccess = reply.data
        console.log('hasaccess', hasaccess)
        if (hasaccess) {
          this.status = "adding"
        }

      } catch (error) {
        console.log('error', error)
        const reply = error.response
        console.error('getting verify_club_access', reply)
        if (reply.status === 401) {
            this.gotoLogin()
        } 
        else {
          this.$root.$emit('snackbar', { text: 'Getting access rules club failed', reason: reply.data.detail })
        }
      }
    },

    async modifyEnrollment(){
      try {
        const reply = await this.$api.club.verify_club_access({
          token: this.logintoken,
          idclub: this.club.idclub,
          role: "InterclubFull"
        })
        hasaccess = reply.data
        console.log('hasaccess', hasaccess)
        if (hasaccess) {
          this.status = "modifying"
        }
      } catch (error) {
        console.log('error', error)
        const reply = error.response
        console.error('getting verify_club_access', reply)
        if (reply.status === 401) {
            this.gotoLogin()
        } 
        else {
          this.$root.$emit('snackbar', { text: 'Getting access rules club failed', reason: reply.data.detail })
        }
      }
    },

    async saveEnrollment(){
      try {
        const reply = await this.$api.interclub.make_enrollment({
          token: this.logintoken,
          idclub: this.club.idclub,
          teams1: this.enrollment.teams1,
          teams2: this.enrollment.teams2,
          teams3: this.enrollment.teams3,
          teams4: this.enrollment.teams4,
          teams5: this.enrollment.teams5,
        })
        console.log('reply', reply.data)
      } catch (error) {
        console.log('error', error)
        const reply = error.response
        console.error('getting make_enrollment', reply)
        if (reply.status === 401) {
            this.gotoLogin()
        } 
        else {
          this.$root.$emit('snackbar', { text: 'Getting save enrollment', reason: reply.data.detail })
        }
      }
    },

  },

  mounted() {
    this.emitInterface();
  },

}
</script>
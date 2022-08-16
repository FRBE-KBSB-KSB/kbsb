<template>
  <v-container>
    <p v-if="!club.idclub">Please select a club to view the access rightrs</p>
    <div v-if="club.idclub">
      <h3 v-show="status_consulting">Consulting access right</h3>
      <h3 v-show="status_modifying">Modifying access rights</h3>
      <v-container>
        <v-row v-show="status_consulting">
          <v-col cols="12" sm="6" md="4">
            <h4>Club Admin</h4>
            All the person listed here, have read+write access to the Club Manager
            <ul>
              <li v-for="m in clubadmin" :key="m">{{ m }}</li>
            </ul>
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <h4>Interclub Admin</h4>
            All the person listed here, have read+write access to the Interclub Manager
            <ul>
              <li v-for="m in interclubadmin" :key="m">{{ m }}</li>
            </ul>
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <h4>Interclub Captain</h4>
            All the person listed here, have read+write access to the planning and results
            of the Interclub.
            <p>This function will become available pnce the playerlist is activated</p>
          </v-col>
        </v-row>
        <v-row v-show="status_consulting">
          <v-btn @click="modifyAccess">Modify access rights</v-btn>
        </v-row>
        <div v-show="status_modifying">
          <h4>Club Admin</h4>
          <h4>Interclub Admin</h4>
          <h4>Interclub Captain</h4>
        </div>
        <div v-show="status_modifying">
          <v-btn @click="saveAccess">Save access rights</v-btn>
          <v-btn @click="cancelAccess">Cancel</v-btn>
        </div>
      </v-container>
    </div>

  </v-container>
</template>
<script>

const ACCESS_STATUS = {
  CONSULTING: 0,
  MODIFYING: 1,
}

const ROLES = ["ClubAdmin", "InterclubAdmin"]

const VISIBILITY = {
  hidden: "HIDDEN",
  club: "CLUB",
  public: "PUBLIC",
}


export default {

  name: 'Access',

  data() {
    return {
      roles: ROLES,
      clubmembers: {},
      clubrights: {},
      clubadmin: [],
      eclubadmin: [],
      interclubadmin: [],
      status: ACCESS_STATUS.CONSULTING,
      visibility_items: Object.values(VISIBILITY).map(x => this.$t(x)),
    }
  },

  props: {
    club: Object
  },

  computed: {
    logintoken() { return this.$store.state.newlogin.value },
    status_consulting() { return this.status == ACCESS_STATUS.CONSULTING },
    status_modifying() { return this.status == ACCESS_STATUS.MODIFYING },
  },

  methods: {

    cancelAccess() {
      this.status = ACCESS_STATUS.CONSULTING
      this.get_clubrights(this.club)
    },

    emitInterface() {
      this.$emit("interface", "get_clubrights", this.get_clubrights);
    },


    last_name(n) {
      const cm = this.clubmembers[n]
      return cm ? cm.last_name : ""
    },

    async get_clubmembers() {
      if (!this.club.id) {
        this.clubmembers = {}
        return
      }
      try {
        const reply = await this.$api.old.get_clubmembers({
          idclub: this.club.idclub,
        })
        const activemembers = reply.data.members
        activemembers.forEach(p => {
          p.merged = `${p.idnumber}: ${p.first_name} ${p.last_name}`
        })
        this.mbr_items = Object.values(activemembers.sort((a, b) =>
          (a.last_name > b.last_name ? 1 : -1)))
        this.clubmembers = Object.fromEntries(this.mbr_items.map(x => [x.idnumber, x]))
      } catch (error) {
        const reply = error.reply
        console.error('Getting club members failed', reply.data.detail)
        this.$root.$emit('snackbar', { text: 'Getting club members failed' })
      }
    },

    async get_clubrights() {
      console.log('getting clubrights')
      await this.get_clubmembers()
      if (!this.club.id) {
        this.clubrights = {}
        return
      }
      try {
        const reply = await this.$api.club.mgmt_get_club({
          id: this.club.id,
          token: this.logintoken
        })
        this.readClubrights(reply.data)
      } catch (error) {
        const reply = error.reply
        if (reply.status === 401) {
          this.$router.push('/mgmt/login')
        }
        else {
          console.error('Getting club details failed', reply.data.detail)
          this.$root.$emit('snackbar', { text: 'Getting club details failed' })
        }
      }
    },

    modifyAccess() {
      this.status = ACCESS_STATUS.MODIFYING
    },

    readClubrights(details) {
      console.log('details', details)
      details.clubroles.forEach((cr) => {
        console.log('cr', cr)
        this.clubrights[cr.nature] = cr.memberlist
      })
      console.log('clubrights', this.clubrights)
      this.clubadmin = this.clubrights["ClubAdmin"].map(
        (x) => {
          let cm = this.clubmembers[x] ? this.clubmembers[x] : {}
          return `${x}: ${cm.first_name} ${cm.last_name}`
        }
      )
      this.interclubadmin = this.clubrights["InterclubAdmin"].map(
        (x) => {
          let cm = this.clubmembers[x] ? this.clubmembers[x] : {}
          return `${x}: ${cm.first_name} ${cm.last_name}`
        }
      )

    },

    async saveAccess() {
      console.log('saving', this.clubrights)
      // try {
      //   const reply = await this.$api.club.mgmt_update_club({
      //     ...this.clubdetails,
      //     token: this.logintoken,
      //   })
      //   this.status = CLUB_STATUS.CONSULTING
      //   this.$root.$emit('snackbar', { text: 'Club saved' })
      // } catch (error) {
      //   const reply = error.response
      //   if (reply.status === 401) {
      //     this.gotoLogin()
      //   }
      //   else {
      //     console.error('Saving enrollment', reply.data.detail)
      //     this.$root.$emit('snackbar', { text: 'Saving enrollment' })
      //   }
      // }
    },

  },

  mounted() {
    this.emitInterface();
    this.$nextTick(() => {
      this.get_clubrights();
    })
  },

}
</script>
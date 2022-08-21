<template>
  <v-container>
    <p v-if="!club.idclub">Please select a club to view the access rights</p>
    <div v-if="club.idclub">
      <h3 v-show="status_consulting">Consulting access right</h3>
      <h3 v-show="status_modifying">Modify access rights</h3>
      <v-container>
        <v-row v-show="status_consulting">
          <v-col cols="12" sm="6" md="4">
            <h4>Club Administrators</h4>
            The club administrators have write access to the Club Manager
            <ul>
              <li v-for="(m, ix) in clubadmin" :key="ix">{{ m }}</li>
            </ul>
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <h4>Interclub Adminstrators</h4>
            The interclub administrators have write access to the Interclub Manager
            <ul>
              <li v-for="(m, ix) in interclubadmin" :key="ix">{{ m }}</li>
            </ul>
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <h4>Interclub Captains</h4>
            The interclub captains have write access to the planning and results
            of the Interclub.
            <p>This function will become available pnce the playerlist is activated</p>
          </v-col>
        </v-row>
        <v-row v-show="status_consulting">
          <v-btn @click="modifyAccess">Modify access rights</v-btn>
        </v-row>
        <div v-show="status_modifying">
          <h4>Club Administrators</h4>
          <ul>
            <li v-for="(m, ix) in clubadmin" :key="m">
              {{ m }} &nbsp; <v-icon @click="deleteClubAdmin(ix)">mdi-delete</v-icon>
            </li>
          </ul>
          <v-autocomplete v-model="newclubadmin" :items="clubmemberitems" @change="addClubAdmin"
            label="Add Member" class="memberselect">
            <template v-slot:item="data">
              {{ data.item.text }}
            </template>
          </v-autocomplete>
          <h4 class="mt-2">Interclub Admin</h4>
          <ul>
            <li v-for="(m, ix) in interclubadmin" :key="m">
              {{ m }} &nbsp; <v-icon @click="deleteInterclubAdmin(ix)">mdi-delete</v-icon>
            </li>
          </ul>
          <v-autocomplete v-model="newinterclubadmin" :items="clubmemberitems"
            @change="addInterclubAdmin" label="Add Member" class="memberselect">
            <template v-slot:item="data">
              {{ data.item.text }}
            </template>
          </v-autocomplete>
          <h4 class="mt-2">Interclub Captain</h4>
          Not available yet
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
import Vue from 'vue'

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
      clubmembers: {},
      clubrights: {},
      clubadmin: {},
      interclubadmin: {},
      interclubcaptain: {},
      newclubadmin: null,
      newinterclubadmin: null,
      newinterclubcaptain: null,
      roles: ROLES,
      status: ACCESS_STATUS.CONSULTING,
      visibility_items: Object.values(VISIBILITY).map(x => this.$t(x)),
    }
  },

  props: {
    club: Object
  },

  computed: {
    clubmemberitems() {
      return Object.entries(this.clubmembers).map(x => {
        return {
          value: x[0],
          text: x[1].merged,
        }
      })
    },
    logintoken() { return this.$store.state.newlogin.value },
    status_consulting() { return this.status == ACCESS_STATUS.CONSULTING },
    status_modifying() { return this.status == ACCESS_STATUS.MODIFYING },
  },

  methods: {


    addClubAdmin() {
      this.clubadmin[this.newclubadmin] = this.clubmembers[this.newclubadmin].merged
      this.$nextTick(() => {
        this.newclubadmin = null
      });
    },

    addInterclubAdmin() {
      this.interclubadmin[this.newinterclubadmin] = this.clubmembers[this.newinterclubadmin].merged
      this.$nextTick(() => {
        this.newinterclubadmin = null
      });
    },

    addInterclubCaptain() {
      this.interclubcaptain[this.newinterclubcaptain] = this.clubmembers[this.newinterclubcaptain].merged
      this.$nextTick(() => {
        this.newinterclubcaptain = null
      });
    },

    cancelAccess() {
      this.status = ACCESS_STATUS.CONSULTING
      this.get_clubrights(this.club)
    },

    deleteClubAdmin(m) {
      // don't delete last member
      if (Object.keys(this.clubadmin).length == 1) return
      Vue.delete(this.clubadmin, m)
    },

    deleteInterclubAdmin(m) {
      // don't delete last member
      if (Object.keys(this.interclubadmin).length == 1) return
      Vue.delete(this.interclubadmin, m)
    },

    deleteInterclubCaptain(m) {
      Vue.delete(this.interclubcaptain, m)
    },

    emitInterface() {
      this.$emit("interface", "get_clubrights", this.get_clubrights);
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
        const members = reply.data.members
        members.forEach(p => {
          p.merged = `${p.idnumber}: ${p.first_name} ${p.last_name}`
        })
        const mbrsorted = members.sort((a, b) =>
          (a.last_name > b.last_name ? 1 : -1))
        this.clubmembers = Object.fromEntries(mbrsorted.map(x => [x.idnumber, x]))
      } catch (error) {
        const reply = error.reply
        if (reply.status == 401) {
          this.gotoLogin()
        }
        else {
          console.error('Getting club members failed', reply.data.detail)
          this.$root.$emit('snackbar', { text: 'Getting club members failed' })
        }
      }
    },

    async get_clubrights() {
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
        if (reply.status == 401) {
          this.gotoLogin()
        }
        else {
          console.error('Getting club details failed', reply.data.detail)
          this.$root.$emit('snackbar', { text: 'Getting club details failed' })
        }
      }
    },

    gotoLogin() {
      this.$router.push('/mgmt/login?url=__mgmt__club')
    },

    modifyAccess() {
      this.status = ACCESS_STATUS.MODIFYING
    },

    readClubrights(details) {
      details.clubroles.forEach((cr) => {
        console.log('cr', cr)
        this.clubrights[cr.nature] = cr.memberlist
      })
      this.clubadmin = Object.fromEntries(this.clubrights["ClubAdmin"].map(
        (x) => {
          let cm = this.clubmembers[x] ? this.clubmembers[x] : {}
          return [x, cm.merged]
        }
      ))
      this.interclubadmin = Object.fromEntries(this.clubrights["InterclubAdmin"].map(
        (x) => {
          let cm = this.clubmembers[x] ? this.clubmembers[x] : {}
          return [x, cm.merged]
        }
      ))
      this.interclubcaptain = Object.fromEntries(this.clubrights["InterclubCaptain"].map(
        (x) => {
          let cm = this.clubmembers[x] ? this.clubmembers[x] : {}
          return [x, cm.merged]
        }
      ))

    },

    async saveAccess() {
      try {
        const reply = await this.$api.club.mgmt_update_club({
          id: this.club.id,
          clubroles: [
            {
              nature: "ClubAdmin",
              memberlist: Object.keys(this.clubadmin)
            },
            {
              nature: "InterclubAdmin",
              memberlist: Object.keys(this.interclubadmin)
            },
            {
              nature: "InterclubCaptain",
              memberlist: Object.keys(this.interclubcaptain)
            },
          ],
          token: this.logintoken,
        })
        this.status = ACCESS_STATUS.CONSULTING
        this.$root.$emit('snackbar', { text: 'Club saved' })
        this.get_clubrights()
      } catch (error) {
        const reply = error.response
        if (reply.status === 401) {
          this.gotoLogin()
        }
        else {
          console.error('Saving access rights failed', reply.data.detail)
          this.$root.$emit('snackbar', { text: 'Saving access rights failed' })
        }
      }
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

<style scoped>
.memberselect {
  max-width: 20em;
}
</style>
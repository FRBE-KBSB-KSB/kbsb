<template>
  <v-container>
    <h1>Club Manager</h1>
    <v-card>
      <v-card-text>
        Select the club. (start typing number of name)
        <v-autocomplete v-model="idclub" :items="clubs" item-text="merged" item-value="idclub"
          color="deep-purple" label="Club" clearable @change="selectclub">
          <template v-slot:item="data">
            {{ data.item.merged }}
          </template>
        </v-autocomplete>
      </v-card-text>
    </v-card>
    <h3 class="mt-2">Selected club: {{ activeclub.idclub }} {{ activeclub.name_short }}
    </h3>
    <div class="elevation-2">

      <v-tabs v-model="tab" color="deep-purple" @change="call_childmethods">
        <v-tabs-slider color="deep-purple"></v-tabs-slider>
        <v-tab>Club details</v-tab>
        <v-tab>Access rights</v-tab>
        <v-tab>Downloads</v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <v-tab-item>
          <MgmtclubDetails @interface="registerChildMethod" :club="activeclub" />
        </v-tab-item>
        <v-tab-item>
          <MgmtclubAccess @interface="registerChildMethod" :club="activeclub" />
        </v-tab-item>
        <v-tab-item>
          <MgmtclubDownloads />
        </v-tab-item>
      </v-tabs-items>
    </div>
  </v-container>
</template>

<script>

const noop = function () { }

export default {

  name: 'Club',

  layout: 'mgmt',

  data() {
    return {
      activeclub: {},
      childmethods: {
        get_clubdetails: noop,
        get_clubrights: noop,
      },
      clubs: [],
      idclub: null,
      tab: null,
    }
  },

  computed: {
    logintoken() { return this.$store.state.newlogin.value }
  },

  head: {
    title: 'Management Clubs',
  },

  mounted() {
    this.$store.commit('newlogin/startup')
    if (!this.logintoken.length) {
      this.gotoLogin()
    }
    this.getClubs()
  },

  methods: {

    call_childmethods() {
      Object.keys(this.childmethods).forEach((v) => {
        this.childmethods[v]()
      })
    },

    async getClubs() {
      try {
        const reply = await this.$api.club.mgmt_get_clubs({
          logintoken: this.logintoken
        })
        this.clubs = reply.data.clubs
        this.clubs.forEach(p => {
          p.merged = `${p.idclub}: ${p.name_short} ${p.name_long}`
        })
      } catch (error) {
        const reply = error.response
        if (reply.status === 401) {
          this.gotoLogin()
        } else {
          console.error('Getting clubs failed', reply.data.detail)
          this.$root.$emit('snackbar', {
            text: 'Getting clubs failed'
          })
        }
      }
    },

    gotoLogin() {
      this.$router.push('/mgmt/login?url=__mgmt__club')
    },

    registerChildMethod(methodname, method) {
      this.childmethods[methodname] = method
    },

    selectclub() {
      if (!this.idclub) {
        this.activeclub = {}
      }
      else {
        this.clubs.forEach((c) => {
          if (c.idclub == this.idclub) {
            this.activeclub = c
          }
        })
      }
      this.$nextTick(() => this.call_childmethods())
    }

  }

}
</script>

<style>
</style>

<template>
  <v-container>
    <h1>Club Manager</h1>
    <v-card>
      <v-card-text>
        {{ $t('Select the club') }} ({{ $t('Start typing number or name') }})
        <v-autocomplete v-model="idclub" :items="clubs" item-text="merged" item-value="idclub"
          color="green" :label="$t('Club')" clearable @change="selectclub">
          <template v-slot:item="data">
            {{ data.item.merged }}
          </template>
        </v-autocomplete>
      </v-card-text>
    </v-card>
    <h3 class="mt-2">{{ $t('Selected club') }}: {{ activeclub.idclub }} {{ activeclub.name_short }}
    </h3>
    <div class="elevation-2">
      <v-tabs v-model="tab" color="green">
        <v-tabs-slider color="green"></v-tabs-slider>
        <v-tab>{{ $t('Details') }}</v-tab>
        <v-tab>{{ $t('Access Rights') }}</v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <v-tab-item>
          <ClubDetails @interface="registerChildMethod" :club="activeclub" />
        </v-tab-item>
        <v-tab-item>
          <ClubAccess @interface="registerChildMethod" :club="activeclub" />
        </v-tab-item>
      </v-tabs-items>
    </div>
  </v-container>
</template>

<script>

const noop = function () { }

export default {

  name: 'Club',

  layout: 'default',

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
    logintoken() { return this.$store.state.oldlogin.value },
  },

  mounted() {
    this.$store.commit('oldlogin/startup')
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
        const reply = await this.$api.club.clb_get_clubs({
          token: this.logintoken
        })
        this.clubs = reply.data.clubs
        this.clubs.forEach(p => {
          p.merged = `${p.idclub}: ${p.name_short} ${p.name_long}`
        })
      } catch (error) {
        const reply = error.response
        switch (reply.status) {
          case 401:
            this.gotoLogin()
            break
          case 403:
            this.$root.$emit('snackbar', { text: this.$t('Permission denied') })
            break
          default:
            console.error('Getting clubs failed', reply.data.detail)
            this.$root.$emit('snackbar', { text: this.$t('Getting clubs failed') })
        }
      }
    },

    gotoLogin() {
      this.$router.push('/tools/oldlogin?url=__tools__club')
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

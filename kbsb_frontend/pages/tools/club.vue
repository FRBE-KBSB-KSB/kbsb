<template>
  <v-container>
    <h1>Club Manager</h1>
    <v-card>
      <v-card-title>
        {{ $t('Select the club') }}
      </v-card-title>
      <v-card-text>
        <div>{{ $t('Start typing to filter (clubnumber or name)') }}</div>
        <v-autocomplete v-model="idclub" :items="clubs" item-text="merged" item-value="idclub" color="green"
          label="Club" clearable @change="selectclub">
          <template v-slot:item="data">
            {{ data.item.merged }}
          </template>
        </v-autocomplete>
      </v-card-text>
    </v-card>
    <h2 class="mt-2">{{ $t('Selected club') }}: {{ activeclub.idclub }} {{ activeclub.name_short }}</h2>
    <div class="elevation-2">

      <v-tabs v-model="tab" color="green">
        <v-tabs-slider color="green"></v-tabs-slider>
        <v-tab>{{ $t('Details') }}</v-tab>
        <v-tab>{{ $t('Access Rights') }}</v-tab>
        <v-tab>{{ $t('Members') }}</v-tab>
        <v-tab>{{ $t('Affiliations') }}</v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <v-tab-item>
          <ClubDetail @interface="registerChildMethod" />
        </v-tab-item>
        <v-tab-item>
          <ClubAccessRights @interface="registerChildMethod" />
        </v-tab-item>
        <v-tab-item>
          <ClubMembers @interface="registerChildMethod" />
        </v-tab-item>
        <v-tab-item>
          <ClubAffiliations @interface="registerChildMethod" />
        </v-tab-item>
        <v-tab-item>
          <InterclubResult @interface="registerChildMethod" />
        </v-tab-item>
      </v-tabs-items>
    </div>
  </v-container>
  </v-container>
</template>

<script>

export default {

  name: 'Club',

  layout: 'default',

  data() {
    return {
      activeclub: {},
      childmethods: {},
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

    editClub(item) {
      this.$router.push('/tools/clubedit/?id=' + item.id)
    },

    registerChildMethod(methodname, method) {
      this.childmethods[methodname] = method
    },

    async getClubs() {
      try {
        const reply = await this.$api.club.get_c_clubs({
          token: this.logintoken
        })
        this.clubs = reply.data.clubs
        this.clubs.forEach(p => {
          p.merged = `${p.idclub}: ${p.name_short} ${p.name_long}`
        })
      } catch (error) {
        const reply = error.response
        console.error('getting get_c_clubs', reply)
        if (reply.status === 401) {
          this.gotoLogin()
        } else {
          console.error('Getting clubs failed', reply.data.detail)
          this.$root.$emit('snackbar', { text: this.$t('Getting clubs failed') })
        }
      }
    },

    gotoLogin() {
      this.$router.push('/tools/oldlogin?url=__tools__club')
    },

    selectclub() {
      if (!this.idclub) {
        this.activeclub = {}
      }
      else {
        this.clubs.forEach(c => {
          if (c.idclub == this.idclub) this.activeclub = c
        })
      }
      this.childmethods.getClubDetails(this.activeclub)
    }

  }

}
</script>

<style>
.lightgreyrow {
  color: #bbb;
}
</style>

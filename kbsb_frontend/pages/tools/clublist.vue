<template>
  <v-container>
    <h1>Club Manager</h1>
    <v-data-table
      :headers="headers"
      :items="clubs"
      :item-class="lightgreyRow"
      :footer-props="footerProps"
      class="elevation-1"
      :sort-by="['name','modified']"
      :search="search"
    >
      <template #top>
        <v-card color="grey lighten-4">
          <v-card-title>
            <v-row class="px-2">
              <v-text-field
                v-model="search"
                label="Search"
                class="mx-4"
                append-icon="mdi-magnify"
                hide_details
              />
              <v-spacer />
              <v-tooltip bottom>
                <template #activator="{ on }">
                  <v-btn
                    fab
                    outlined
                    color="green"
                    v-on="on"
                    @click="refresh()"
                  >
                    <v-icon>mdi-refresh</v-icon>
                  </v-btn>
                </template>
                Refresh
              </v-tooltip>
            </v-row>
          </v-card-title>
        </v-card>
      </template>
      <template #item._creationtime="{ item }">
        {{ (new Date(item._creationtime)).toLocaleDateString($i18n.locale, { dateStyle: 'medium' }) }}
      </template>
      <template #item.guestlist="{ item }">
        {{ item.guestlist.length }}
      </template>
      <template #item.payment_id="{ item }">
        <NuxtLink
          v-if="item.payment_id"
          :to="'/mgmt/paymentrequestedit?id=' + item.payment_id"
        >
          link
        </NuxtLink>
      </template>
      <template #item.action="{ item }">
        <v-tooltip bottom>
          <template #activator="{ on }">
            <v-icon small class="mr-2" v-on="on" @click="editClub(item)">
              mdi-pencil
            </v-icon>
          </template>
          Edit Club
        </v-tooltip>
        <v-tooltip v-if="item.payment_id" bottom>
          <template #activator="{ on }">
            <v-icon small class="mr-2" v-on="on" @click="gotoPaymentRequest(item)">
              mdi-currency-eur
            </v-icon>
          </template>
          Show payment request
        </v-tooltip>
      </template>
      <template #no-data>
        No clubs found.
      </template>
    </v-data-table>
  </v-container>
</template>

<script>

export default {

  name: 'Clublist',

  layout: 'default',

  data () {
    return {
      footerProps: {
        itemsPerPageOptions: [150, -1]
      },
      headers: [
        {
          text: 'Club nr', value: 'idclub'
        },
        {
          text: 'Long name', value: 'name_long'
        },
        {
          text: 'Short name', value: 'name_short'
        },
        {
          text: 'Contact email', value: 'email_main'
        },
        {
          text: 'Actions', value: 'action', sortable: false
        }
      ],
      clubs: [],
      search: ''
    }
  },

  computed: {
    oldlogin () { return this.$store.state.oldlogin.value }
  },

  mounted () {
    this.$store.commit('oldlogin/startup')
    if (!this.oldlogin.length) {
      this.gotoLogin()
    }
    this.getClubs()
  },

  methods: {

    editClub (item) {
      this.$router.push('/tools/clubedit/?id=' + item.id)
    },


    async getClubs () {
      console.log('getClubs', this.oldlogin)
      try {
        const reply = await this.$api.club.get_c_clubs({
          token: this.oldlogin
        })
        console.log('reply', reply.data)
        this.clubs = reply.data.clubs
      } catch (error) {
        const reply = error.replyonse
        console.error('getting get_c_clubs', reply)
        if (reply.status === 401) {
            this.gotoLogin()
        } else {
          this.$root.$emit('snackbar', { text: 'Getting clubs failed', reason: reply.data.detail })
        }
      }
    },

    gotoLogin() {
        this.$router.push('/tools/oldlogin?url=__tools__clublist')
    },

    lightgreyRow (item) {
      if (!item.enabled) {
        return 'lightgreyrow'
      }
    },

    async refresh () {
      await this.getClubs()
    }

  }

}
</script>

<style>
.lightgreyrow {
  color: #bbb;
}
</style>

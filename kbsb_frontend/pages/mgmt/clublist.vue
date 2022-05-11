<template>
  <v-container>
    <h1>Management Clubs</h1>
    <v-data-table
      :headers="headers"
      :items="clubs"
      :footer-props="footerProps"
      class="elevation-1"
      :sort-by="['name','modified']"
    >
      <template #top>
        <v-card color="grey lighten-4">
          <v-card-title>
            <v-row class="px-2">
              <v-spacer />
              <v-tooltip bottom>
                <template #activator="{ on }">
                  <v-btn
                    fab
                    outlined
                    color="deep-purple"
                    v-on="on"
                    @click="addClub()"
                  >
                    <v-icon>mdi-plus</v-icon>
                  </v-btn>
                </template>
                Add Club
              </v-tooltip>
            </v-row>
          </v-card-title>
        </v-card>
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

  layout: 'mgmt',

  data () {
    return {
      filter: {},
      footerProps: {
        itemsPerClubOptions: [20, 50, -1],
        itemsPerClub: 20
      },
      headers: [
        {
          text: 'Nr', value: 'idclub'
        },
        {
          text: 'Long name', value: 'name'
        },
        {
          text: 'Short name', value: 'doctype'
        },
        {
          text: 'Actions', value: 'action', sortable: false
        }
      ],
      clubs: []
    }
  },

  computed: {
    token () { return this.$store.state.token.value }
  },

  mounted () {
    this.getClubs()
  },

  methods: {

    addClub () {
      this.$router.push('/mgmt/clubadd')
    },

    editClub (item) {
      this.$router.push('/mgmt/clubedit/?id=' + item.id)
    },

    async getClubs () {
      try {
        const resp = await this.$api.club.get_clubs({
          token: this.token
        })
        this.clubs = resp.data.clubs
      } catch (error) {
        const resp = error.response
        console.error('getting getClubs', resp)
        if (resp.status === 401) {
          this.$router.push('/mgmt/login')
        } else {
          this.$root.$emit('snackbar', { text: 'Getting clubs failed', reason: resp.data.detail })
        }
      }
    }

  }

}
</script>

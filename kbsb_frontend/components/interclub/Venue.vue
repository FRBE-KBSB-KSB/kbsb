<template>
  <v-container>
    <p v-if="!club.idclub">{{ $t('Please select a club to view the interclub venues') }}</p>
    <div v-if="club.idclub">
      <h3>{{ $t('Interclub venues') }}</h3>
      <div v-show="!venues.length && status_consulting">
        <p>{{ $t('No interclub venue is defined yet') }}</p>
      </div>
      <div v-show="status_consulting">
        <v-card v-for="(v, ix) in venues" :key="ix" class="elevation-4 my-2">
          <v-card-title>
            {{ $t('Venue') }}: {{ ix + 1 }}
          </v-card-title>
          <v-card-text>
            <div><b>{{ $t('Address') }}:</b> <br />
              <span v-html="v.address.split('\n').join('<br />')"></span>
            </div>
            <div><b>{{ $t('Email address') }}:</b> {{ v.email }}</div>
            <div><b>{{ $t('Telephone number') }}:</b> {{ v.phone }}</div>
            <div><b>{{ $t('Capacity (boards)') }}:</b> {{ v.capacity }}</div>
            <div><b>{{ $t('Not available') }}:</b> {{ v.notavailable.join(', ') }}</div>
          </v-card-text>
        </v-card>
        <v-btn @click="modifyVenues">
          {{ $t('Modify venues') }}
        </v-btn>
      </div>
      <v-container v-show="status_modifying">
        <v-row v-for="(v, ix) in venues" :key="ix" class="elevation-4 my-2">
          <v-col cols="12" sm="5">
            <h4>{{ $t('Venue') }}: {{ ix + 1 }}</h4>
            <v-textarea v-model="v.address" :label="$t('Address')" rows="3" @input="addEmptyVenue"
              outlined />
            <v-text-field v-model="v.email" :label="$t('Email address')" />
            <v-text-field v-model="v.phone" :label="$t('Telephone number')" />
            <v-text-field v-model="v.capacity" :label="$t('Capacity (boards)')" type="number"
              min="1" max="99" />
          </v-col>
          <v-col cols="12" sm="5">
            <h4>{{ $t('Availability') }}</h4>
            <v-radio-group v-model="v.available">
              <v-radio value="all" :label="$t('All rounds')" />
              <v-radio value="selected"
                :label="$t('The venue is not available on following rounds')" />
            </v-radio-group>
            <v-select multiple v-show="v.available != 'all'" :items="rounds" chips
              v-model="v.notavailable"
              :label="$t('Select the rounds the venue is not available')" />
          </v-col>
          <v-col cols="12" sm="2">
            <v-btn fab small @click="deleteVenue(ix)" v-show="ix < venues.length - 1">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </v-col>
        </v-row>
        <v-row>
          <v-btn @click="saveVenues">
            {{ $t('Save Venues') }}
          </v-btn>
          <v-btn @click="cancelVenues">
            {{ $t('Cancel') }}
          </v-btn>
        </v-row>
      </v-container>
    </div>

  </v-container>
</template>
<script>
const VENUE_STATUS = {
  CONSULTING: 0,
  MODIFYING: 1,
}
const ROUNDS = {
  1: "2022-09-25",
  2: "2022-10-16",
  3: "2022-11-06",
  4: "2022-11-20",
  5: "2022-12-05",
  6: "2023-01-29",
  7: "2023-02-12",
  8: "2023-03-05",
  9: "2023-03-19",
  10: "2023-04-16",
  11: "2023-04-30",
}

const empty_venue = {
  address: "",
  available: "all",
  notavailable: [],
  capacity: 99,
  email: "",
  phone: "",
}

export default {

  name: 'Venue',

  data() {
    return {
      status: VENUE_STATUS.CONSULTING,
      rounds: Object.entries(ROUNDS).map(x => ({ value: x[1], text: `R${x[0]}: ${x[1]}` })),
      venues: [],
    }
  },

  props: {
    club: Object
  },

  computed: {
    logintoken() { return this.$store.state.oldlogin.value },
    status_consulting() { return this.status == VENUE_STATUS.CONSULTING },
    status_modifying() { return this.status == VENUE_STATUS.MODIFYING },
  },

  methods: {

    addEmptyVenue() {
      console.log('addEmpty Venue')
      const last = this.venues[this.venues.length - 1]
      if (!last || last.address !== '') {
        this.venues.push({ ...empty_venue })
      }
    },

    cancelVenues() {
      this.status = VENUE_STATUS.CONSULTING
      this.find_interclubvenues()
    },

    deleteVenue(ix) {
      this.venues.splice(ix, 1)
      this.addEmptyVenue()
    },

    emitInterface() {
      this.$emit("interface", "find_interclubvenues", this.find_interclubvenues);
    },

    async find_interclubvenues() {
      console.log('running find_interclubvenues', this.club)
      if (!this.club.id) {
        this.venues = []
        return
      }
      try {
        const reply = await this.$api.interclub.find_interclubvenues({
          idclub: this.club.idclub
        })
        console.log('get venues', reply.data)
        this.readVenues(reply.data ? reply.data.venues : [])
      } catch (error) {
        const reply = error.response
        console.error('Getting interclub venues failed', reply.data.detail)
        this.$root.$emit('snackbar', { text: this.$t('Getting interclub venues failed') })
      }
    },

    async modifyVenues() {
      try {
        const reply = await this.$api.club.verify_club_access({
          token: this.logintoken,
          idclub: this.club.idclub,
          role: "InterclubAdmin"
        })
        this.status = VENUE_STATUS.MODIFYING
        this.addEmptyVenue()
      } catch (error) {
        const reply = error.response
        switch (reply.status) {
          case 401:
            this.gotoLogin()
            break;
          case 403:
            this.$root.$emit('snackbar', { text: this.$t("You don't have the access right to perfom this action") })
            break;
          default:
            console.error('Getting accessrules club failed', reply.data.detail)
            this.$root.$emit('snackbar', { text: this.$t('Getting accessrules club failed') })
        }
      }
    },

    readVenues(venues) {
      this.venues = []
      venues.forEach((v) => {
        v.available = v.notavailable.length ? "selected" : "all"
        this.venues.push(v)
      })
    },

    async saveVenues() {
      try {
        console.log('Saving venues')
        let savedvenues = []
        this.venues.forEach(v => {
          if (v.address && v.address.length) {
            let { available, ...others } = v
            savedvenues.push(others)
          }
        })
        console.log('savedvenues', savedvenues)
        const reply = await this.$api.interclub.set_interclubvenues({
          token: this.logintoken,
          idclub: this.club.idclub,
          venues: savedvenues,
        })
        this.status = VENUE_STATUS.CONSULTING
        this.find_interclubvenues()
      } catch (error) {
        const reply = error.response
        switch (reply.status) {
          case 401:
            this.gotoLogin()
            break
          case 403:
            this.$root.$emit('snackbar', {
              text: this.$t("You don't have the access rights to perform this action")
            })
            break
          default:
            console.error('Getting interclub venues failed', reply.data.detail)
            this.$root.$emit('snackbar', { text: this.$t('Getting interclub venues failed') })
        }
      }
    },


  },

  mounted() {
    this.emitInterface();
    this.$nextTick(() => {
      this.find_interclubvenues();
    })
  },

}
</script>
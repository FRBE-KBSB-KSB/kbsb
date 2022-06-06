<template>
  <v-container>
    <v-row>
      <h2>Edit Reservation {{ rsv.number }}: {{ rsv.last_name }} {{ rsv.first_name }}</h2>
      <v-spacer />
      <v-tooltip bottom>
        <template #activator="{ on }">
          <v-btn
            slot="activator"
            outlined
            fab
            color="deep-purple"
            v-on="on"
            @click="back()"
          >
            <v-icon>mdi-arrow-left</v-icon>
          </v-btn>
        </template>
        <span>Go Back</span>
      </v-tooltip>
    </v-row>
    <v-card class="my-3">
      <v-card-title>
        Properties
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6">
            <v-text-field v-model="rsv.last_name" label="Last name" />
            <v-text-field v-model="rsv.first_name" label="First name" />
            <v-textarea v-model="rsv.address" label="Address" />
            <v-textarea v-model="rsv.bycco_remarks" label="Remarks from Bycco" />
            <v-text-field v-model="rsv.checkindate" label="Checkin Date" />
            <v-text-field v-model="rsv.checkoutdate" label="Checkout Date" />
          </v-col>
          <v-col cols="12" sm="6">
            <v-switch v-model="rsv.enabled" label="Enabled" color="deep-purple" />
            <p>Reservation created: {{ rsv._creationtime }}</p>
            <p>Reservation modified: {{ rsv._modificationtime }}</p>
            <v-text-field v-model="rsv.email" label="E-mail" />
            <v-text-field v-model="rsv.mobile" label="Mobile" />
            <v-textarea v-model="rsv.remarks" label="Customer Remarks" />
            <v-text-field v-model="rsv.locale" label="Language" />
            <v-text-field v-model="rsv.lodging" label="Requested accomodation" />
            <v-text-field v-model="rsv.meals" label="Requested meals" />
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="saveProperties">
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
    <v-card class="my-3">
      <v-card-title>Guest List</v-card-title>
      <v-card-text>
        <v-row v-for="(g, ix) in rsv.guestlist" :key="ix" class="mt-2">
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              v-model="g.first_name"
              dense
              label="First name"
            />
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              v-model="g.last_name"
              dense
              label="Last name"
            />
          </v-col>
          <v-col cols="12" sm="6" md="2">
            <v-text-field
              v-model="g.birthday"
              dense
              label="Birthdate"
            />
          </v-col>
          <v-col cols="6" sm="3" md="2">
            <v-checkbox v-model="g.player" dense label="player" />
          </v-col>
          <v-col cols="6" sm="3" md="2">
            <v-btn fab small dark color="deep-purple" @click="deleteGuest(ix)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </v-col>
        </v-row>
        <h4>New guest</h4>
        <v-row class="mt-2">
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              v-model="newguest.first_name"
              dense
              label="First name"
            />
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              v-model="newguest.last_name"
              dense
              label="Last name"
            />
          </v-col>
          <v-col cols="12" sm="6" md="2">
            <v-text-field
              v-model="newguest.birthday"
              dense
              label="Birthdate"
            />
          </v-col>
          <v-col cols="6" sm="3" md="2">
            <v-checkbox v-model="newguest.player" dense label="player" />
          </v-col>
          <v-col cols="6" sm="3" md="2">
            <v-btn fab small dark color="deep-purple" @click="addGuest">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="saveGuestlist">
          Save
        </v-btn>
      </v-card-actions>
    </v-card>

    <v-card class="my-3">
      <v-card-title>Assignment of room</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="3">
            <v-select
              v-model="assignment.roomtype"
              :items="roomtypes"
              label="Select roomtype"
              @change="roomtypeSelected"
            />
          </v-col>
          <v-col cols="3">
            <v-select
              v-model="assignment.roomnumber"
              :items="roomnumbers"
              label="Select room number"
              :disabled="!assignment.roomtype.length"
            />
          </v-col>
          <v-col cols="3">
            <v-select
              v-model="assignment.modroomtype"
              :items="roomtypes"
              label="Modify roomtype"
              :disabled="!assignment.roomtype.length"
            />
          </v-col>
          <v-col cols="3">
            <v-btn :disabled="!assignment.roomnumber.length" @click="confirm_assignment">
              confirm
            </v-btn>
          </v-col>
        </v-row>
        <h4>Existing Assignments</h4>
        <div v-for="(a,ix) in rsv.assignments" :key="ix">
          {{ a.roomnr }} {{ a.roomtype }} &nbsp;&nbsp;&nbsp;
          <v-btn @click="deleteAssignment(ix)">
            Delete
          </v-btn>
        </div>
        <h4 class="mt-2">
          Payment Request
        </h4>
        <v-btn v-if="!rsv.payment_id" @click="create_pr">
          Create
        </v-btn>
        <v-btn v-if="rsv.payment_id" :to="'/mgmt/paymentrequestedit?id=' + rsv.payment_id">
          Show
        </v-btn>
        <v-btn v-if="rsv.payment_id" @click="delete_pr">
          Delete
        </v-btn>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>

export default {

  name: 'Reservationedit',

  layout: 'mgmt',

  data () {
    return {
      assignment: {
        roomtype: '',
        roomnumber: '',
        modroomtype: null
      },
      dialogDelete: false,
      idreservation: this.$route.query.id,
      newguest: {},
      period: {},
      roomtypes: [],
      roomnumbers: [],
      rsv: {}
    }
  },

  async fetch () {
    const common = await this.$content('common').fetch()
    this.roomtypes = Array.from(Object.keys(common.roomtypes),
      (x) => { return { value: x, text: common.roomtypes[x] } })
    this.period = common.period
  },

  computed: {
    token () { return this.$store.state.token.value }
  },

  mounted () {
    this.getReservation()
  },

  methods: {

    addGuest () {
      this.rsv.guestlist.push({
        last_name: this.newguest.last_name,
        first_name: this.newguest.first_name,
        birthday: this.newguest.birthday,
        player: this.newguest.player
      })
      this.newguest = {}
    },

    back () {
      this.$router.go(-1)
    },

    async create_pr () {
      try {
        const resp = await this.$api.reservation.create_pr({
          id: this.$route.query.id,
          token: this.token
        })
        this.$router.push('/mgmt/paymentrequestedit/?id=' + resp.data)
      } catch (error) {
        const resp = error.response
        console.error('creating payment request', resp)
        if (resp.status === 401) {
          this.$router.push('/mgmt/login')
        } else {
          this.$root.$emit('snackbar', { text: 'Creating paymentrequesr failed', reason: resp.data.detail })
        }
      }
    },

    async delete_pr () {
      if (confirm('Are you sure to delete the linked payment request')) {
        try {
          await this.$api.reservation.delete_pr({
            id: this.$route.query.id,
            token: this.token
          })
          this.getReservation()
        } catch (error) {
          const resp = error.response
          console.error('deleting linked payment request', resp)
          if (resp.status === 401) {
            this.$router.push('/mgmt/login')
          } else {
            this.$root.$emit('snackbar', { text: 'Deleting Paymentrequest failed', reason: resp.data.detail })
          }
        }
      }
    },

    async confirm_assignment () {
      const as = this.assignment
      const mrt = (as.modroomtype && as.modroomtype !== as.roomtype)
        ? this.assignment.modroomtype
        : null
      console.log('mrt', mrt, as)
      try {
        const resp = await this.$api.reservation.assign_room({
          id: this.$route.query.id,
          roomnumber: as.roomnumber,
          token: this.token,
          roomtype: mrt
        })
        this.readReservation(resp.data)
      } catch (error) {
        const resp = error.response
        console.error('getting assigning room', resp)
        if (resp.status === 401) {
          this.$router.push('/mgmt/login')
        } else {
          this.$root.$emit('snackbar', { text: 'Assigning room failed', reason: resp.data.detail })
        }
      }
    },

    async deleteAssignment (ix) {
      try {
        const resp = await this.$api.reservation.unassign_room({
          id: this.$route.query.id,
          roomnumber: this.rsv.assignments[ix].roomnr,
          token: this.token
        })
        this.readReservation(resp.data)
      } catch (error) {
        const resp = error.response
        console.error('getting unassigning room', resp)
        if (resp.status === 401) {
          this.$router.push('/mgmt/login')
        } else {
          this.$root.$emit('snackbar', { text: 'Assigning room failed', reason: resp.data.detail })
        }
      }
    },

    deleteGuest (ix) {
      this.rsv.guestlist.splice(ix, 1)
    },

    async getReservation () {
      try {
        const resp = await this.$api.reservation.get_reservation({
          id: this.$route.query.id,
          token: this.token
        })
        this.readReservation(resp.data)
      } catch (error) {
        const resp = error.response
        console.error('getting getReservations', resp)
        if (resp.status === 401) {
          this.$router.push('/mgmt/login')
        } else {
          this.$root.$emit('snackbar', { text: 'Getting reservation failed', reason: resp.data.detail })
        }
      }
    },

    readReservation (reservation) {
      this.rsv = { ...reservation }
      this.assignment = { roomtype: '', roomnumber: '' }
    },

    async roomtypeSelected () {
      console.log('calling roomtypeSelected')
      try {
        const rooms = (await this.$api.reservation.get_free_rooms({
          roomtype: this.assignment.roomtype
        })).data.rooms
        console.log('returned rooms', rooms)
        this.roomnumbers = Array.from(Object.keys(rooms), x => rooms[x].number)
      } catch (error) {
        console.error('getting free rooms', error.response)
      }
    },

    async saveProperties () {
      console.log('saving props reservation')
      try {
        await this.$api.reservation.update_reservation({
          id: this.$route.query.id,
          reservation: {
            address: this.rsv.address,
            bycco_remarks: this.rsv.bycco_remarks,
            checkindate: this.rsv.checkindate,
            checkoutdate: this.rsv.checkoutdate,
            email: this.rsv.email,
            enabled: this.rsv.enabled,
            first_name: this.rsv.first_name,
            last_name: this.rsv.last_name,
            locale: this.rsv.locale,
            lodging: this.rsv.lodging,
            meals: this.rsv.meals,
            mobile: this.rsv.mobile,
            organizers: this.rsv.organizers,
            remarks: this.rsv.remarks
          },
          token: this.token
        })
        console.log('save successful')
        this.$root.$emit('snackbar', { text: 'Reservation saved' })
      } catch (error) {
        const resp = error.response
        console.error('getting getReservations', resp)
        if (resp.status === 401) {
          this.$router.push('/mgmt/login')
        } else {
          this.$root.$emit('snackbar', { text: 'Saving reservation failed', reason: resp.data.detail })
        }
      }
    },

    async saveGuestlist () {
      console.log('saving props reservation')
      try {
        await this.$api.reservation.update_reservation({
          id: this.$route.query.id,
          reservation: {
            guestlist: this.rsv.guestlist
          },
          token: this.token
        })
        console.log('save successful')
        this.$root.$emit('snackbar', { text: 'Reservation saved' })
      } catch (error) {
        const resp = error.response
        console.error('getting getReservations', resp)
        if (resp.status === 401) {
          this.$router.push('/mgmt/login')
        } else {
          this.$root.$emit('snackbar', { text: 'Saving preservation failed', reason: resp.data.detail })
        }
      }
    }

  }

}
</script>

<style scoped>
.bordermd {
  border: 1px solid grey;
}
.v-input--checkbox { margin-top:0; }
</style>

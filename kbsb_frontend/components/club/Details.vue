<template>
  <v-container>
    <p v-if="!club.idclub">{{ $t('Select a club to view the club details') }}</p>
    <div v-if="club.idclub">
      <h3 v-show="status_consulting">{{ $t('Consulting club details') }}</h3>
      <h3 v-show="status_modifying">{{ $t('Modify club') }}</h3>
      <v-container>
        <v-row v-show="status_consulting">
          <v-col cols="12" md="6">
            <h4>{{ $t('Club details') }}</h4>
            <div><span class="fieldname">{{ $t('Long name') }}</span>: {{ clubdetails.name_long }}
            </div>
            <div><span class="fieldname">{{ $t('Short name') }}</span>: {{ clubdetails.name_short }}
            </div>
            <div><span class="fieldname">{{ $t('Federation') }}</span>: {{ clubdetails.federation }}
            </div>
            <div><span class="fieldname">{{ $t('Club venue') }}</span>:<br />
              <span v-html='clubdetails.venue.replace("\n", "<br />")'></span>
            </div>
            <div><span class="fieldname">{{ $t('Website') }}</span>: {{ clubdetails.website }}</div>
            <div><span class="fieldname">{{ $t('Bank account name') }}</span>: {{
                clubdetails.bankaccount_name
            }}
            </div>
            <div><span class="fieldname">{{ $t('Bank account IBAN') }}</span>: {{
                clubdetails.bankaccount_iban
            }}
            </div>
            <div><span class="fieldname">{{ $t('Bank account BIC') }}</span>: {{
                clubdetails.bankaccount_bic
            }}
            </div>
            <h4 class="mt-2">{{ $t('Contact') }}</h4>
            <div><span class="fieldname">{{ $t('Main email address') }}</span>: {{
                clubdetails.email_main
            }}
            </div>
            <div><span class="fieldname">{{ $t('Email address Interclub') }}</span>: {{
                clubdetails.email_intercLub
            }}</div>
            <div><span class="fieldname">{{ $t('Email address administration') }}</span>: {{
                clubdetails.email_admin
            }}</div>
            <div><span class="fieldname">{{ $t('Email address finance') }}</span>: {{
                clubdetails.email_finance
            }}
            </div>
            <div><span class="fieldname">{{ $t('Postal address') }}</span>:<br />
              <span v-html='clubdetails.address.replace("\n", "<br />")'></span>
            </div>
          </v-col>
          <v-col cols="12" sm="6" lg="4">
            <h4>{{ $t('Board members') }}</h4>
            <ul>
              <li v-for="(bm, f) in clubdetails.boardmembers" :key="f">
                <span class="fieldname">{{ boardroles[f][$i18n.locale] }}</span>:
                {{ bm.first_name }} {{ bm.last_name }}<br />
                email: {{ bm.email }}<br />
                gsm: {{ bm.mobile }}
              </li>
            </ul>
          </v-col>
        </v-row>
        <v-row v-show="status_consulting">
          <v-btn @click="modifyClub">{{ $t('Modify club') }}</v-btn>
        </v-row>
        <v-row v-show="status_modifying">
          <v-col cols="12" md="6">
            <h4>{{ $t('Club details') }}</h4>
            <v-text-field v-model="clubdetails.name_long" label="Long name" />
            <v-text-field v-model="clubdetails.name_short" label="Short name" />
            <v-text-field v-model="clubdetails.federation" label="Federation (V/F/D)" />
            <v-textarea v-model="clubdetails.venue" label="Venue" />
            <v-text-field v-model="clubdetails.website" label="Website" />
          </v-col>
          <v-col cols="12" md="6">
            <h4>{{ $t('Contact') }}</h4>
            <v-text-field v-model="clubdetails.email_main" label="Main E-mail address" />
            <v-text-field v-model="clubdetails.email_intercub" label="E-mail Interclub" />
            <v-text-field v-model="clubdetails.email_admin" label="E-mail administration" />
            <v-text-field v-model="clubdetails.email_finance" label="E-mail finance" />
            <v-textarea v-model="clubdetails.address" label="Postal address" />
          </v-col>

          <v-col cols="12" md="6">
            <h4>{{ $t('Bank details') }}</h4>
            <v-text-field v-model="clubdetails.bankacount_name" label="Name bank account" />
            <v-text-field v-model="clubdetails.bankaccount_iban" label="IBAN bank account" />
            <v-text-field v-model="clubdetails.bankaccount_bic" label="BIC bank account" />
          </v-col>
        </v-row>
        <div v-show="status_modifying">
          <h4>{{ $t('Board members') }}</h4>
          <v-row v-for="(bm, f) in boardroles" :key="f">
            <!-- <span class="fieldname">{{ boardroles[f][$i18n.locale] }}</span>: -->
            <v-col cols="12" sm="6" lg="4">
              <v-autocomplete v-model="boardmembers[f].idnumber" :items="mbr_items"
                :label="boardroles[f][$i18n.locale]" item-text="merged" item-value="idnumber"
                color="deep-purple" clearable @change="updateboard(f)">
                <template v-slot:item="data">
                  {{ data.item.merged }}
                </template>
              </v-autocomplete>
            </v-col>
            <v-col cols="12" sm="6" lg="4">
              {{ bm.email }}
              <v-select v-model="boardmembers[f].email_visibility" :items="visibility_items"
                color="deep-purple" @change="updateboard(f)" label="Email visibility" />
            </v-col>
            <v-col cols="12" sm="6" lg="4">
              {{ bm.mobile }}
              <v-select v-model="boardmembers[f].mobile_visibility" :items="visibility_items"
                color="deep-purple" @change="updateboard(f)" label="Mobile visibility" />
            </v-col>
          </v-row>
          <v-row>
            <v-btn @click="saveClub">{{ $t('Save club') }}</v-btn>
            <v-btn @click="cancelClub">{{ $t('Cancel') }}</v-btn>
          </v-row>
        </div>
      </v-container>
    </div>
  </v-container>
</template>
<script>

const CLUB_STATUS = {
  CONSULTING: 0,
  MODIFYING: 1,
}

const EMPTY_CLUBDETAILS = {
  venue: "",
  address: "",
}

const EMPTY_BOARD = {
  president: { idnumber: 0 },
  vice_president: { idnumber: 0 },
  secretary: { idnumber: 0 },
  treasurer: { idnumber: 0 },
  tournament_director: { idnumber: 0 },
  youth_director: { idnumber: 0 },
  interclub_director: { idnumber: 0 },
  webmaster: { idnumber: 0 },
  bar_manager: { idnumber: 0 },
  press_officer: { idnumber: 0 },
}

const VISIBILITY = {
  hidden: "HIDDEN",
  club: "CLUB",
  public: "PUBLIC",
}

export default {

  name: 'Details',

  data() {
    return {
      boardroles: [],
      boardmembers: EMPTY_BOARD,
      clubmembers: {},
      clubdetails: {},
      mbr_items: [],
      status: CLUB_STATUS.CONSULTING,
      visibility_items: Object.values(VISIBILITY).map(x => this.$t(x)),
    }
  },

  props: {
    club: Object
  },

  computed: {
    logintoken() { return this.$store.state.oldlogin.value },
    status_consulting() { return this.status == CLUB_STATUS.CONSULTING },
    status_modifying() { return this.status == CLUB_STATUS.MODIFYING },
  },

  methods: {

    cancelClub() {
      this.status = CLUB_STATUS.CONSULTING
      this.getClubDetails(this.club)
    },

    emitInterface() {
      this.$emit("interface", "get_clubdetails", this.get_clubdetails);
    },

    async fetch() {
      this.boardroles = (await this.$content('boardroles').fetch()).boardroles
    },

    async get_clubmembers() {
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
        if (reply.status === 401) {
          this.gotoLogin()
        }
        else {
          console.error('Getting club members failed', reply.data.detail)
          this.$root.$emit('snackbar', { text: this.$t('Getting club members failed') })
        }
      }
    },

    async get_clubdetails() {
      if (!this.club.id) {
        this.clubdetails = EMPTY_CLUBDETAILS
        return
      }
      try {
        const reply = await this.$api.club.clb_get_club({
          id: this.club.id,
          token: this.logintoken
        })
        this.readClubdetails(reply.data)
      } catch (error) {
        const reply = error.reply
        if (reply.status === 401) {
          this.gotoLogin()
        }
        else {
          console.error('Getting club details failed', reply.data.detail)
          this.$root.$emit('snackbar', { text: this.$t('Getting club details failed') })
        }
      }
    },

    gotoLogin() {
      this.$router.push('/mgmt/login?url=__tools__club')
    },

    modifyClub() {
      this.status = CLUB_STATUS.MODIFYING
      this.get_clubmembers();

    },

    readClubdetails(details) {
      this.clubdetails = { ...details }
      if (!this.clubdetails.address) this.clubdetails.address = ""
      if (!this.clubdetails.venue) this.clubdetails.venue = ""
      this.boardmembers = { ...EMPTY_BOARD, ...details.boardmembers }
    },

    async saveClub() {
      console.log('saving', this.clubdetails)
      try {
        const reply = await this.$api.club.clb_update_club({
          ...this.clubdetails,
          token: this.logintoken,
        })
        this.status = CLUB_STATUS.CONSULTING
        this.$root.$emit('snackbar', { text: this.$t('Club saved') })
      } catch (error) {
        const reply = error.response
        if (reply.status === 401) {
          this.gotoLogin()
        }
        else {
          console.error('Saving enrollment', reply.data.detail)
          this.$root.$emit('snackbar', { text: this.$t('Saving enrollment') })
        }
      }
    },

    updateboard(f) {
      const bm = this.boardmembers[f]
      if (bm.idnumber) {
        let cm = this.clubmembers[bm.idnumber]
        bm.first_name = cm.first_name
        bm.last_name = cm.last_name
        bm.email = cm.email
        bm.mobile = cm.mobile
        if (!bm.email_visibility) bm.email_visibility = "CLUB"
        if (!bm.mobile_visibility) bm.mobile_visibility = "CLUB"
        this.clubdetails.boardmembers[f] = bm
      }
      else {
        bm.first_name = null
        bm.last_name = null
        bm.email = null
        bm.mobile = null
        bm.email_visibility = null
        bm.mobile_visibility = null
        delete this.clubdetails.boardmembers[f]
      }

    },

  },

  mounted() {
    this.emitInterface();
    this.fetch();
    this.$nextTick(() => {
      this.get_clubdetails();
    })
  },

}
</script>

<style scoped>
.fieldname {
  color: green;
}
</style>
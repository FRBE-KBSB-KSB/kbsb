// <script setup>

// import { INTERCLUBS_STATUS, STOPDATE, empty_enrollment } from '@/util/interclubs.js'

// export default {

//   name: 'Enrollment',

//   data() {
//     return {
//       grouping: [
//         { "text": this.$t("No preference"), "value": "0" },
//         { "text": this.$t("1 group"), "value": "1" },
//         { "text": this.$t("2 opposite groups"), "value": "2" },
//       ],
//       splitting: [
//         { "text": this.$t("In 1 series"), "value": "1" },
//         { "text": this.$t("In multiple series"), "value": "2" },
//       ],
//       enrollment: empty_enrollment,
//       rules: {
//         count20: (x) => (x && x.length <= 20 || 'Max 20 characters')
//       },
//       status: INTERCLUBS_STATUS.CONSULTING,
//       stopdate: STOPDATE,
//     }
//   },

//   props: {
//     club: Object,
//   },

//   computed: {
//     logintoken() { return this.$store.state.oldlogin.value },
//     groupingvalue() {
//       const gr = this.grouping.filter(x => x.value == this.enrollment.wishes.grouping)
//       return gr.length > 0 ? gr[0].text : ""
//     },
//     splittingvalue() {
//       const spl = this.splitting.filter(x => x.value == this.enrollment.wishes.split)
//       return spl.length > 0 ? spl[0].text : ""
//     },
//     status_consulting() { return this.status == INTERCLUBS_STATUS.CONSULTING },
//     status_modifying() { return this.status == INTERCLUBS_STATUS.MODIFYING },
//   },

//   methods: {

//     cancelEnrollment() {
//       this.status = INTERCLUBS_STATUS.CONSULTING
//       this.find_interclubenrollment()
//     },

//     async find_interclubenrollment() {
//       if (!this.club.id) {
//         this.enrollment = empty_enrollment
//         return
//       }
//       this.enrollment = { ... empty_enrollment}
//       try {
//         const reply = await this.$api.interclub.find_interclubenrollment({
//           idclub: this.club.idclub
//         })
//         if (reply.data) {
//           this.enrollment = reply.data
//           if (!this.enrollment.name.length) this.enrollment.name = this.club.name_short
//         }
//         else {
//           this.enrollment.id = null
//         }
//       } catch (error) {
//         const reply = error.response
//         if (reply.status === 401) {
//           this.gotoLogin()
//         }
//         else {
//           console.error('Getting existing enrollment failed', reply.data.detail)
//           this.$root.$emit('snackbar', { text: this.$t('Getting existing enrollment failed') })
//         }
//       }
//     },

//     async modifyEnrollment() {
//       try {
//         const reply = await this.$api.club.verify_club_access({
//           token: this.logintoken,
//           idclub: this.club.idclub,
//           role: "InterclubAdmin"
//         })
//         this.status = INTERCLUBS_STATUS.MODIFYING
//         this.enrollment.name = this.club.name_short
//       } catch (error) {
//         const reply = error.response
//         switch (reply.status) {
//           case 401:
//             this.gotoLogin()
//             break;
//           case 403:
//             this.$root.$emit('snackbar', { text: this.$t("You don't have the access right to perfom this action") })
//             break;
//           default:
//             console.error('Getting accessrules club failed', reply.data.detail)
//             this.$root.$emit('snackbar', { text: this.$t('Getting accessrules club failed') })
//         }
//       }
//     },

//     async saveEnrollment() {
//       try {
//         const reply1 = await this.$api.interclub.set_interclubenrollment({
//           token: this.logintoken,
//           idclub: this.club.idclub,
//           name: this.enrollment.name,
//           teams1: this.enrollment.teams1,
//           teams2: this.enrollment.teams2,
//           teams3: this.enrollment.teams3,
//           teams4: this.enrollment.teams4,
//           teams5: this.enrollment.teams5,
//           wishes: this.enrollment.wishes,
//         })
//         this.status = INTERCLUBS_STATUS.CONSULTING
//         this.find_interclubenrollment(this.club)
//       } catch (error) {
//         const reply = error.response
//         switch (reply.status) {
//           case 401:
//             this.gotoLogin()
//             break;
//           case 403:
//             this.$root.$emit('snackbar', { text: this.$t("You don't have the access right to perfom this action") })
//             break;
//           default:
//             console.error('Getting accessrules club failed', reply.data.detail)
//             this.$root.$emit('snackbar', { text: this.$t('Saving enrollment failed') })
//         }        
//       }
//     },

//     async setupEnrollment(){
//       await this.find_interclubenrollment()
//     },

//   },

// }
// </script>
// <template>
//   <v-container>
//     <h2>{{ $t('Interclubs enrollment') }}</h2>
//     <p v-if="!club.idclub">{{ $t('Please select a club to view the enrollment') }}</p>
//     <div v-if="club.idclub">
//       <v-container v-show="status_consulting">
//         <v-row v-show="!enrollment.id">
//           <v-col cols="12" sm="6" md="4" xl="3">
//             <v-card class="elevation-5">
//               <v-card-title class="card-title">
//                 {{ $t("Enrollment") }}
//               </v-card-title>
//               <v-card-text>
//                 {{ $t('The club is not enrolled yet') }}
//               </v-card-text>
//             </v-card>
//           </v-col>
//         </v-row>
//         <v-row v-show="enrollment.id">
//           <v-col cols="12" sm="6" md="4" xl="3">
//             <v-card class="elevation-5">
//               <v-card-title class="card-title">
//                 {{ $t("Teams") }}
//               </v-card-title>
//               <v-card-text>
//                 <ul>
//                   <li>{{ $t('Teams in division') }} 1: {{ enrollment.teams1 }}</li>
//                   <li>{{ $t('Teams in division') }} 2: {{ enrollment.teams2 }}</li>
//                   <li>{{ $t('Teams in division') }} 3: {{ enrollment.teams3 }}</li>
//                   <li>{{ $t('Teams in division') }} 4: {{ enrollment.teams4 }}</li>
//                   <li>{{ $t('Teams in division') }} 5: {{ enrollment.teams5 }}</li>
//                 </ul>
//               </v-card-text>
//             </v-card>
//           </v-col>
//           <v-col cols="12" sm="6" md="4" xl="3">
//             <v-card class="elevation-5">
//               <v-card-title class="card-title">
//                 {{ $t("Wishes") }}
//               </v-card-title>
//               <v-card-text>
//                 <ul>
//                   <li>{{ $t('Teams grouped by pairing number') }}: {{ groupingvalue }} </li>
//                   <li>{{ $t('Distribution of teams in same division') }}: {{ splittingvalue }} </li>
//                   <li>{{ $t('Regional preferences') }}: {{ enrollment.wishes.regional }} </li>
//                   <li>{{ $t('Remarks') }}: {{ enrollment.wishes.remarks }} </li>
//                 </ul>
//               </v-card-text>
//             </v-card>
//           </v-col>
//           <v-col cols="12" sm="6" md="4" xl="3">
//             <v-card class="elevation-5">
//               <v-card-title class="card-title">
//                 {{ $t("Name") }}
//               </v-card-title>
//               <v-card-text>
//                 {{ $t('Name of the club as shown in results and pairings')  }}: {{ enrollment.name }}
//               </v-card-text>
//             </v-card>
//           </v-col>
//         </v-row>
//         <v-row>
//           <v-btn @click="modifyEnrollment" :disabled="new Date() > stopdate">
//             {{ $t('Edit') }}
//           </v-btn>
//         </v-row>
//       </v-container>
//       <v-container v-show="status_modifying">
//         <v-row>
//           <v-col cols="12" sm="6" md="4" xl="3">
//             <v-card class="elevation-5">
//               <v-card-title class="card-title">
//                 {{ $t('Teams') }}
//               </v-card-title>
//               <v-card-text>
//                 <p>{{ $t('Number of teams per division') }}</p>
//                 <v-text-field v-model="enrollment.teams1" :label="$t('Division') + ' 1'"
//                   type="number" min="0" max="1" />
//                 <v-text-field v-model="enrollment.teams2" :label="$t('Division') + ' 2'"
//                   type="number" min="0" max="15" />
//                 <v-text-field v-model="enrollment.teams3" :label="$t('Division') + ' 3'"
//                   type="number" min="0" max="15" />
//                 <v-text-field v-model="enrollment.teams4" :label="$t('Division') + ' 4'"
//                   type="number" min="0" max="15" />
//                 <v-text-field v-model="enrollment.teams5" :label="$t('Division') + ' 5'"
//                   type="number" min="0" max="15" />
//               </v-card-text>
//             </v-card>
//           </v-col>
//           <v-col cols="12" sm="6" md="4" xl="3">
//             <v-card class="elevation-5">
//               <v-card-title class="card-title">
//                 {{ $t('Wishes') }}
//               </v-card-title>
//               <v-card-text>
//                 <div>{{ $t('Teams grouped by pairing number') }}</div>
//                 <v-select :label="$t('Grouping')"
//                   v-model="enrollment.wishes.grouping" :items="grouping" />
//                 <div>{{ $t('Distribution of teams in same division') }}</div>   
//                 <v-select :label="$t('Distribution')"
//                   v-model="enrollment.wishes.split" :items="splitting" />
//                 <div>{{ $t('Regional preferences') }}</div>
//                 <v-text-field v-model="enrollment.wishes.regional"
//                   :label="$t('Regional')" /> 
//                 <v-textarea rows="5" v-model="enrollment.wishes.remarks" :label="$t('Other wishes')" />
//               </v-card-text>                                                     
//             </v-card>            
//           </v-col>
//           <v-col cols="12" sm="6" md="4" xl="3">
//             <v-card class="elevation-5">
//               <v-card-title class="card-title">
//                 {{ $t('Name') }}
//               </v-card-title>
//               <v-card-text>
//                 {{ $t('You can define a name for your club when the results and standings are displayed.') }}
//                 {{ $t('As a default, your clubname is used.') }} 
//                 <v-text-field v-model="enrollment.name" :label="$t('Name')" maxlength="20" :rules="[rules.count20]"/>
//               </v-card-text>                                                     
//             </v-card>            
//           </v-col>
//         </v-row>
//         <v-row>
//           <v-btn @click="saveEnrollment">
//             {{ $t('Save') }}
//           </v-btn>&nbsp;
//           <v-btn @click="cancelEnrollment">
//             {{ $t('Cancel') }}
//           </v-btn>
//         </v-row>
//       </v-container>
//     </div>
//   </v-container>
// </template>

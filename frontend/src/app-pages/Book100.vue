<template>

  <v-container class="mt-1 markedcontent">
    <h1>{{ $t('Ordering the book 100 years of Belgian chess history') }}</h1>
    <div v-html="$t(general)" />
    <h3>{{ $t('Distribution points') }}</h3>
    <div v-html="$t(delivery)" />
    <h3>{{ $t('Ordering form') }}</h3>
    <v-row>
      <v-col cols=12 sm=6 md=4> 
        <h4>{{ $t('Identity') }}</h4>
        <v-text-field v-model="id_bel" :label="$t('ID RBCF')"
          append-icon="mdi-magnify" @click:append="search" />
        <v-text-field :label="$t('First name')" v-model="first_name" />
        <v-text-field :label="$t('Last name')" v-model="last_name" />
      </v-col>
      <v-col cols=12 sm=6 md=4> 
        <h4>{{ $t('Contact details') }}</h4>
        <v-text-field :label="$t('E-mail')" v-model="email" />
        <v-text-field :label="$t('Mobile phone')" v-model="mobile" />
        <v-textarea :label="$t('Address')" v-model="address" rows=3 />        
      </v-col>
      <v-col cols=12 sm=6 md=4> 
        <h4>{{ $t('Which versions do you want?') }}</h4>
        <v-checkbox :label="$t('Dutch')" v-model="nl"  @change="recalculate" />
        <v-checkbox :label="$t('French')" v-model="fr"  @change="recalculate" />
        <v-checkbox :label="$t('German')" v-model="de"  @change="recalculate" />
      </v-col>
      <v-col cols=12 sm=6 md=4> 
        <h4>{{ $t('Delivery') }}</h4>
        <v-radio-group v-model="distribution" @change="recalculate">
          <v-radio label="Luc Cornet" value="luc" />
          <v-radio label="Bernard Malfliet" value="bernard" />
          <v-radio label="Ruben Decrop" value="ruben" />
          <v-radio label="Philippe Vukojevic" value="philippe" />
          <v-radio label="Laurent Wery" value="laurent" />
          <v-radio label="DPD (+ 6.20 Euro) " value="dpd" />
        </v-radio-group>
      </v-col>
    </v-row>
    <p>{{ $t('Cost') }}: {{ calccost}} Euro</p>
    <v-btn @click="confirm">{{ $t('Confirm') }}</v-btn>
        
    <div v-if="confirmed">
      <p class="mt-3">{{ $t('Order created successfully') }}</p>
      <div v-html="$t(emailconfirmation)" />
    </div>  
  </v-container>

</template>

<script>

import {mapState} from "vuex"
import * as moment from 'moment';



export default {

  name: 'Book100',

  data () {return {
    address: '',
    confirmed: false,
    cost: 0,
    de: false,
    distribution: '',
    email: '',
    first_name: '',
    found: false,
    fr: false,
    id_bel: '',
    last_name: '',
    mobile: '',
    nl: false,

    general: 
`<p>If your are an affilated player you can buy the book 100 years of Belgian
chess history for the low price of 10 Euro. Non affilated persons can buy 
the book for 15 Euro.</p> 
<p>The book is available in 3 languages:  
Dutch, French and German.</p>
<p>If you are an affiliated player, don't forget to provide your 
RBCF ID and to click on the search button.  Your name will be filled in 
automatically</p>`.replace(/(\r\n|\n|\r)/gm, ""),

    delivery: 
`<p>In order to keep the costs low, you can pick the books from 5 members 
of the board.  You have to contact that person and agree on where and when 
the book can be handed over.</p>
<p>The board members are:</p>
<ul>
<li>Luc Cornet, covering provinces of Limburg and Liège
<li>Bernard Malfliet, covering provinces of Oost-Vlaanderen cost, and Vlaams Brabant
<li>Ruben Decrop, covering provinces of Antwerp and West-Vlaanderen
<li>Philippe Vukojevic, covering provinces of Namur and Luxembourg
<li>Laurent Wery, covering Brussels and provinces of Hainaut and Brabant Wallon
</ul>
<p>See the <a href='/page/board'>Board page</a> for the contact details.</p> 
<p>Alternatively we can deliver the book at any address in Belgium by DPD at 
an additional cost of 6.20 Euro </p>`.replace(/(\r\n|\n|\r)/gm, ""),

    emailconfirmation: 
`<p>In a few minutes you will receive an confirmation e-mail for your order.
The e-mail will include the payment instructions.</p>
<p>If you selected one of the board members for the delivery, you will 
find the contact details in this e-mail.</p>`.replace(/(\r\n|\n|\r)/gm, "")
  }},

  computed: {
    ...mapState(['locale', 'api']),
    calccost (){
      return this.cost.toFixed(2);
    }
  },

  methods: {

    confirm() {
      let self=this, books=[];
      if (this.nl) books.push('nl');
      if (this.fr) books.push('fr');
      if (this.de) books.push('de');
      this.api.createBook100(
        {},{requestBody: {
          id_bel: this.id_bel,
          address: this.address,
          books: books.join(','),
          cost: this.cost,
          distribution: this.distribution,
          email: this.email,
          first_name: this.first_name,
          last_name: this.last_name,
          mobile: this.mobile,
        }}
      ).then(
        function(data) {
          console.log('order created', data.obj)
          self.confirmed =  true;
        },
        function(data){
          console.error('failed order creating', data);
          self.$root.$eremit('snackbar', {
            text: self.this.$t('Failed creating order for book'),
          });
        }
      );

    },

    recalculate() {
      let cost, books=[];
      if (this.nl) books.push('nl');
      if (this.fr) books.push('fr');
      if (this.de) books.push('de');
      cost = books.length * (this.found ? 10.0: 15.0);
      if (this.distribution == 'dpd') cost += 6.20;
      this.cost = cost;
    },

    search () {
      let self=this;
      this.api.getMemberAnon(
        {id: this.id_bel},
      ).then(
        function(data) {
          console.log('member found', data.obj)
          self.found =  true;
          self.first_name = data.obj.first_name;
          self.last_name = data.obj.last_name;
        },
        function(data){
          if (data.status == 404) {
            self.$root.$emit('snackbar', {
              text: self.$t('Member not found'), 
            })            
          }
          else {
            console.error('getting getMember', data);
            self.$root.$emit('snackbar', {
              text: self.this.$t('Getting member failed'),
            })            
          }
        }
      );

    },
   
  },

  mounted () {
    moment.locale(this.locale)
  },

}
</script>


<style scoped>

.markedcontent table {
  border-collapse: collapse;
  min-width: 30em;
}

.markedcontent table {
  border: 1px solid black;
}

.markedcontent td {
  border: 1px solid black;
  padding: 6px;
}

.markedcontent  th {
  border: 1px solid black;
  padding: 6px;
}

</style>

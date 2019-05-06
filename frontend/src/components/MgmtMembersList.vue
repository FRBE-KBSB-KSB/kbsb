<template>
<v-container fluid grid-list-md class="elevation-1">
  <v-layout row>
    <v-flex>
        <h1>Management Members</h1>
    </v-flex>
    <v-flex>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="gotoAdd()" slot="activator">
          <v-icon>add</v-icon>
        </v-btn>
        <span>New member</span>
      </v-tooltip>
      <v-tooltip bottom>
        <v-btn outline fab color="green" href="/trn/csv" slot="activator">
          <v-icon>cloud_download</v-icon>
        </v-btn>
        <span>CSV download</span>
      </v-tooltip>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="gotoGroups()" slot="activator">
          <v-icon>group</v-icon>
        </v-btn>
        <span>Groups and Roles</span>
      </v-tooltip>
    </v-flex>
  </v-layout>

  <v-layout row wrap>
    <v-flex sm4 xs6>
      <v-text-field append-icon="search" @click:append="search" v-model="ss" />
    </v-flex>
    <v-flex sm4 xs6>
      <v-select :items="catitems" v-model="catselected" @change="changeCat()" />
    </v-flex>
  </v-layout>

  <v-data-table :items="members" class="elevation-1" :headers="headers"
                :rows-per-page-items="[25,50,100]" :pagination.sync="pagination">
    <template slot="headers" slot-scope="props" >
      <th v-for="header in props.headers" :key="header.text"
          :class="headerClasses(header)" @click="changeSort(header)">
        {{ header.text }}
        <v-icon small v-show="header.sortable">arrow_upward</v-icon>
      </th>
      <th class="text-xs-left">Actions</th>
    </template>
    <template slot="items" slot-scope="props">
      <td>{{ props.item.id }}</td>
      <td>{{ props.item.first_name }}</td>
      <td>{{ props.item.last_name }}</td>
      <td>
        <v-icon class="mr-1" @click="editMember(props.item)">edit</v-icon>
        <v-icon class="mr-1" @click="photoMember(props.item)">face</v-icon>
      </td>
    </template>
  </v-data-table>

</v-container>
</template>

<script>

import api from '../util/api'

export default {
  name: "MgmtMembersList",

  props: ['ts', 'selection'],

  computed: {

    headers () { return [
      {
        text: 'ID',
        align: 'left',
        sortable: true,
        value: 'id'
      },
      {
        text: 'First name',
        align: 'left',
        sortable: true,
        value: 'first_name'
      },
      {
        text: 'Last name',
        align: 'left',
        sortable: true,
        value: 'last_name'
      },
    ]},

  },


  data () {return {
    catitems: [
      {value: '', text: 'All'},
      {value: 'BRD', text: 'Board'},
      {value: 'MAN', text: 'Mandated persons'},
      {value: 'SPO', text: 'Sport commission'},
      {value: 'APP', text: 'Appeal commission '},
      {value: 'VSF', text: 'VSF'},
      {value: 'FEFB', text: 'FEFB'},
      {value: 'SVDB', text: 'SVDB'},
      {value: 'BCF', text: 'Brussels Federation'},
      {value: 'WVL', text: 'West-Vlaanderen'},
      {value: 'OVL', text: 'Oost-Vlaanderen'},
      {value: 'ANT', text: 'Antwerpen'},
      {value: 'VLB', text: 'Vlaams Brabant'},
      {value: 'LIM', text: 'Limburg'},
      {value: 'BRW', text: 'Brabant Wallon'},
      {value: 'LIE', text: 'Liège'},
      {value: "HAI", text: 'Hainaut'},
      {value: "NALUX", text: 'Namur - Luxembourg'},
    ],
    catselected: 'All',
    pagination: {
      sortBy: 'last_name',
      descending: false,
    },
    members: [],
    selected: [],
    ss: '',
  }},

  methods: {
    changeCat () {
      this.getMembers();
    },

    changeSort (header) {
      if (!header.sortable) return;
      if (this.pagination.sortBy === header.value) {
        this.pagination.descending = !this.pagination.descending
      } else {
        this.pagination.sortBy = header.value;
        this.pagination.descending = false
      }
    },

    editMember(m) {
      this.$emit('update', { section: 'edit', member: m, })
    },

    getMembers () {
      api('getMembers', {
        cat: this.catselected,
        ss: this.ss.length ? this.ss : null,
      }).then(
        function(data) {
          this.members = data.members;
        }.bind(this)
      );
    },

    gotoAdd () {
      this.$emit('update', {section: 'add'})
    },

    gotoGroups () {
      this.$emit('update', {section: 'groups'})
    },

    headerClasses (header) {
      let hc = ['column'];
      hc.push(header.align ? 'text-xs-' + header.align : 'text-xs-left');
      hc.push(header.sortable ? 'sortable': '');
      hc.push(this.pagination.descending ? 'desc' : 'asc');
      hc.push(header.value === this.pagination.sortBy ? 'active' : '');
      return hc;
    },

    photoMember(m) {
      this.$emit('update', { section: 'photo', member: m, })
    },

    search () {
      this.getMember();
    },

  },

  mounted () {
    this.getMembers();
  },

  watch: {
    ts: function(){
      this.getMembers();
    }
  }

}
</script>

<style scoped>

</style>
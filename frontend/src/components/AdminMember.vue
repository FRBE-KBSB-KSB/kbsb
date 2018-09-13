<template>
<div>

  <h1>Management members</h1>
  <v-tabs v-model="tabix" class="mt-2" slider-color="green darken-2">
    <v-tab active-class="default-class green lighten-4">Members</v-tab>
    <v-tab active-class="default-class green lighten-4">Detail</v-tab>
    <v-tab active-class="default-class green lighten-4">Photo</v-tab>
  </v-tabs>

  <v-tabs-items v-model="tabix">
    <v-tab-item>
      <admin-member-list :mbrs="mbrs" @updatembr="updatembr">
      </admin-member-list>
    </v-tab-item>
    <v-tab-item>
      <admin-member-detail :mbr="currentMbr" :mode="mode" @updatembr="updatembr">
      </admin-member-detail>
    </v-tab-item>
    <v-tab-item>
      <h3 class="mt-2">Photo</h3>
      <p>To DO</p>
    </v-tab-item>
  </v-tabs-items>

</div>
</template>

<script>
import api from '../api/api';
import AdminMemberList from './AdminMemberList';
import AdminMemberDetail from './AdminMemberDetail';

export default {
  name: "AdminMember",
  components: {
    "admin-member-list": AdminMemberList,
    "admin-member-detail": AdminMemberDetail,
  },
  data () {
    return {
      tabix: 0,
      mbrs: [],
      currentMbr: {'org': [{}, {}, {}]},
      mode: 'add',
    }
  },
  methods: {
    getmbrs () {
      var self = this;
      api('getMembers').then(
        function (data) {
          self.mbrs = [];
          data.members.forEach(function(m, ix) {
              if (m.org)
                while (m.org.length < 3) {
                    m.org.push({})
                }
              m.oldidbel = m.idbel + '';
          });
          console.log('members', data.members);
          self.mbrs = data.members
        },
        function (data) {
          console.error('getting members failed', data)
        }
      );
      this.tabix = "0";
    },
    updatembr (cmd, param) {
      switch (cmd) {
        case 'add':
          this.mode = 'add';
          this.currentMbr = {'org': [{}, {}, {}]},
          this.tabix = 1;
          break;
        case 'edit':
          this.mode = 'edit';
          this.currentMbr = param;
          this.tabix = 1;
          break;
        case 'list':
          this.getmbrs()
          this.tabix = 0;
          break;
        case 'photo':
          this.currentMbr = param;
          this.tabix = 2;
          break;
        }
    }
  },
  mounted () {
    this.getmbrs();
  },

}
</script>

<style scoped>

</style>
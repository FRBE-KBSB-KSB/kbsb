<template>
  <v-container class="mt-1">
    <h1>{{ $t('Board') }}</h1>
    <h2>{{ $t("Board members") }}</h2>
    <v-row>
      <v-col v-for="bm in board" :key="bm.email" cols="12" md="6" xl="4">
        <div class="ma-1 elevation-3 d-flex pa-1">
          <div class="flex-shrink-0 flex-grow-0">
            <img :src="'/board/' + bm.email + '.jpg'" class="person-photo d-none d-lg-flex">
            <img :src="'/board/' + bm.email + '.jpg'" class="person-photo-sm d-lg-none ">
          </div>
          <div class="d-flex flex-column flex-grow-1 ml-1">
            <div class="green lighten-3 pa-3">
              {{ bm.first_name }} {{ bm.last_name }}
            </div>
            <div class="pa-3">
              <div v-for="r in bm.roles" :key="r">
                {{ r }}
              </div>
              <div v-show="bm.mobile">
                tel: {{ bm.mobile }}
              </div>
              <div>e-mail: {{ bm.email }}@frbe-kbsb.be</div>
            </div>
            <div class="pa-3 d-flex">
              <v-btn v-show="bm.mobile" text icon class="green darken-2 mx-2" :href="'tel:' + bm.mobile">
                <v-icon color="white">
                  mdi-phone
                </v-icon>
              </v-btn>
              <v-btn v-show="bm.mobile" text icon class="green darken-2 mx-2" :href="'sms:' + bm.mobile">
                <v-icon color="white">
                  mdi-message-processing
                </v-icon>
              </v-btn>
              <v-btn text icon class="green darken-2 mx-2" :href="'mailto:' + bm.email + '@frbe-kbsb-ksb.be'">
                <v-icon color="white">
                  mdi-email
                </v-icon>
              </v-btn>
            </div>
          </div>
        </div>
      </v-col>
    </v-row>
    <h2 class="mt-3">
      {{ $t("Collaborator") }}
    </h2>
    <v-row>
      <v-col v-for="bm in collaborator" :key="bm.email" cols="12" md="6" xl="4">
        <div class="ma-1 elevation-3 d-flex pa-1">
          <div class="flex-shrink-0 flex-grow-0">
            <img :src="'/board/' + bm.email + '.jpg'" class="person-photo d-none d-lg-flex">
            <img :src="'/board/' + bm.email + '.jpg'" class="person-photo-sm d-lg-none ">
          </div>
          <div class="d-flex flex-column flex-grow-1 ml-1">
            <div class="green lighten-3 pa-3">
              {{ bm.first_name }} {{ bm.last_name }}
            </div>
            <div class="pa-3">
              <div v-for="r in bm.roles" :key="r">
                {{ r }}
              </div>
              <div v-show="bm.mobile">
                tel: {{ bm.mobile }}
              </div>
              <div>e-mail: {{ bm.email }}@frbe-kbsb.be</div>
            </div>
            <div class="pa-3 d-flex">
              <v-btn v-show="bm.mobile" text icon class="green darken-2 mx-2" :href="'tel:' + bm.mobile">
                <v-icon color="white">
                  mdi-phone
                </v-icon>
              </v-btn>
              <v-btn v-show="bm.mobile" text icon class="green darken-2 mx-2" :href="'sms:' + bm.mobile">
                <v-icon color="white">
                  mdi-message-processing
                </v-icon>
              </v-btn>
              <v-btn text icon class="green darken-2 mx-2" :href="'mailto:' + bm.email + '@frbe-kbsb-ksb.be'">
                <v-icon color="white">
                  mdi-email
                </v-icon>
              </v-btn>
            </div>
          </div>
        </div>
      </v-col>
    </v-row>
    <h2 class="mt-3">
      {{ $t("Ombudsman") }}
    </h2>
    <v-row>
      <v-col v-for="bm in ombudsman" :key="bm.email" cols="12" md="6" xl="4">
        <div class="ma-1 elevation-3 d-flex pa-1">
          <div class="flex-shrink-0 flex-grow-0">
            <img :src="'/board/' + bm.email + '.jpg'" class="person-photo d-none d-lg-flex">
            <img :src="'/board/' + bm.email + '.jpg'" class="person-photo-sm d-lg-none ">
          </div>
          <div class="d-flex flex-column flex-grow-1 ml-1">
            <div class="green lighten-3 pa-3">
              {{ bm.first_name }} {{ bm.last_name }}
            </div>
            <div class="pa-3">
              <div v-for="r in bm.roles" :key="r">
                {{ r }}
              </div>
              <div v-show="bm.mobile">
                tel: {{ bm.mobile }}
              </div>
              <div>e-mail: {{ bm.email }}@frbe-kbsb.be</div>
            </div>
            <div class="pa-3 d-flex">
              <v-btn v-show="bm.mobile" text icon class="green darken-2 mx-2" :href="'tel:' + bm.mobile">
                <v-icon color="white">
                  mdi-phone
                </v-icon>
              </v-btn>
              <v-btn v-show="bm.mobile" text icon class="green darken-2 mx-2" :href="'sms:' + bm.mobile">
                <v-icon color="white">
                  mdi-message-processing
                </v-icon>
              </v-btn>
              <v-btn text icon class="green darken-2 mx-2" :href="'mailto:' + bm.email + '@frbe-kbsb-ksb.be'">
                <v-icon color="white">
                  mdi-email
                </v-icon>
              </v-btn>
            </div>
          </div>
        </div>
      </v-col>
    </v-row>
    <h2 class="mt-3">
      {{ $t("Honorary member") }}
    </h2>
    <ul>
      <li v-for="bm in honorary" :key="bm.last_name">
        {{ bm.first_name }} {{ bm.last_name }}
      </li>
    </ul>
    <h2 class="mt-3">
      {{ $t("Honorary president") }}
    </h2>
    <ul>
      <li
        v-for="bm in honorpres"
        :key="bm.last_name"
      >
        {{ bm.first_name }} {{ bm.last_name }}
      </li>
    </ul>
  </v-container>
</template>

<script>

export default {

  async asyncData ({ $content }) {
    const members = await $content('board').fetch()
    const board = members.filter(m => m.category === 'board')
    const collaborator = members.filter(m => m.category === 'collaborator')
    const ombudsman = members.filter(m => m.category === 'ombudsman')
    const honorary = members.filter(m => m.category === 'honorary')
    const honorpres = members.filter(m => m.category === 'honorpres')
    return {
      board, collaborator, ombudsman, honorary, honorpres
    }
  }

}
</script>

<style scoped>

.person-photo {
  width: 160px;
}

.person-photo-sm {
  width: 120px;
}

</style>

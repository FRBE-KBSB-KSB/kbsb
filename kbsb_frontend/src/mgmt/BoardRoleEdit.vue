<template>
<v-container class="elevation-1 mt-2">
  <v-row>
    <v-col cols=12 sm=6>
        <h1>Edit board role: {{ name }} </h1>
    </v-col>
    <v-col col=12 sm=6>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" outlined fab color="deep-purple" @click="back()" 
              slot="activator">
            <v-icon>mdi-arrow-left</v-icon>
          </v-btn>
        </template>
        <span>Go Back</span>
      </v-tooltip>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" outlined fab color="deep-purple" @click="save()" 
              slot="activator">
            <v-icon>mdi-content-save</v-icon>
          </v-btn>
        </template>
        <span>Save board role properties</span>
      </v-tooltip>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" outlined fab color="deep-purple" @click="remove()" 
              slot="activator">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
        <span>Delete board role</span>
      </v-tooltip>
    </v-col>
  </v-row>
  <v-row>
    <v-col cols=12 sm=6>
      <v-text-field label="Name" v-model="br.name" />
    </v-col>
  </v-row>
  <h4>Translations</h4>
  <v-tabs class="elevation-2" >
    <v-tab v-for="l in languages" :key="l">
      {{ l }}
    </v-tab>
    <v-tab-item v-for="l in languages" :key="l">
      <v-text-field class="mx-3" v-model='titles[l]' label="Title" />
    </v-tab-item>
  </v-tabs>    
</v-container>
</template>

<script>

import { mapState } from 'vuex'
import { bearertoken } from "@/util/token"
import { locales } from '@/util/lang'


// const BoardRolePond = vueBoardRolePond();

export default {

  name: "BoardRoleEdit",

  computed: {
    ...mapState(['token', 'api']),
  },

  data () {return {
    br: {},
    name: '',
    languages: locales, 
    titles: {},
  }},

  methods: {

    back () {
      this.$router.push('/mgmt/boardrole/list');
    },

    getBoardRole() {
      let self=this;
      this.api.getBoardRole(
        {id: this.$route.params.id},
        {securities: bearertoken(this.token)},
      ).then(
        function(data) {
          self.readBoardRole(data.obj);
        },
        function(data){
          console.error('failed get boardrole', data)
          self.$root.$emit('snackbar', {text: 'Getting boardrole failed', reason: data})          
        }
      );
    },

    readBoardRole (boardrole) {
      let titles = {default: boardrole.title.default.value};
      this.br = boardrole;
      this.name = this.br.name + '';
      console.log('brt', boardrole.title)
      locales.forEach(l => titles[l] = boardrole.title[l] ? boardrole.title[l].value : '')
      this.titles = titles
    },

    remove () {
      let self=this;
      if (window.confirm('Are you sure to delete boardrole "' + this.name + '"?')) {
        this.api.delete_boardrole(
          { id: this.$route.params.id },
          {securities: bearertoken(this.token)},
        ).then(
          function(){
            // TODO show deleted
            console.log('successfully deleted boardrole')
            self.back();
          }, 
          function(data){
            // TODO show error message
            console.error('failed to delete', data);
          }
        );
      }
    },

    save () {
      let self=this;
      const {id, ...boardrole} = this.br;
      console.log('filling ', boardrole);
      locales.forEach(l => boardrole.title[l] = {value: self.titles[l]})      
      console.log('saving', boardrole);
      this.api.updateBoardRole({id},{
        requestBody: boardrole,
        securities: bearertoken(this.token),        
      }).then(
        function(){
          // TODO successfully saved
          console.log('successfully saved board role')
          self.$root.$emit('snackbar', {text: 'Board role saved'})          
        },
        function(data){
          // TODO show error message
          console.error('failed to save', data);
          self.$root.$emit('snackbar', {text: 'Saving board role failed', reason: data})          
          self.back();
        }
      );
    },

  },

  mounted () {
    this.getBoardRole();
  }

}
</script>

<style scoped>
.bordermd {
  border: 1px solid grey;
}
</style>
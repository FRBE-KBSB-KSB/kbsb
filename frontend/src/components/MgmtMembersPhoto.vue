<template>
<v-container fluid grid-list-md class="elevation-1">
 
  <v-layout row wrap>
    <v-flex>
      <h1>Photo Member: {{ fullname }} </h1>
    </v-flex>
    <v-flex>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="back()" slot="activator">
          <v-icon>arrow_back</v-icon>
        </v-btn>
        <span>Go Back</span>
      </v-tooltip>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="crop()" slot="activator">
          <v-icon>crop</v-icon>
        </v-btn>
        <span>Crop image</span>
      </v-tooltip>      
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="save()" slot="activator">
          <v-icon>save</v-icon>
        </v-btn>
        <span>Save</span>
      </v-tooltip>
      <v-tooltip bottom>
        <v-btn outline fab color="green" @click="gotoEdit()" slot="activator">
          <v-icon>edit</v-icon>
        </v-btn>
        <span>Save</span>
      </v-tooltip>            
    </v-flex>
  </v-layout>
 
  <v-layout row wrap>
    <v-flex class="my-1">
      <h4>Existing Photo</h4>
      <div><img :src="photosrc"></div>
    </v-flex>
    <v-flex class="my-1">
      <h4>Resulting Photo</h4>
      <div><img :src="photo"></div>
    </v-flex>
  </v-layout>

  <div class="mt-2">
    <h4>Drop Area</h4>
    <file-pond ref="pond" accepted-file-types="image/jpeg, image/png"
        @addfile="handleFile" className="dropbox" /> 
  </div>
  
  <div  class="mt-2">
    <h4>Photo Selection</h4>
    <div class="photosrc">
      <vue-cropper ref='photosrc' :view-mode="2" drag-mode="crop" :auto-crop-area="0.5"
                  :background="true" src="" alt="Source Image" :aspect-ratio="0.8"
                  preview="#photoresult" :img-style="{height: '400px'}">
      </vue-cropper>
    </div>        
  </div>

</v-container>
</template>

<script>

import api from '../util/api'
import 'filepond/dist/filepond.min.css';
import DateFormatted from "./DateFormatted";
import VueCropper from 'vue-cropperjs';
import vueFilePond from 'vue-filepond';

const FilePond = vueFilePond();

export default {
  name: "MgmtPartPhoto",

  components: {
    DateFormatted,
    VueCropper,
    FilePond,
  },

  props: ['member'],

  computed :  {
    fullname () {
      return this.member.first_name + ' ' + this.member.last_name;
    },
  },

  data () {return {
    p: {},
    photosrc: '',
    photo: '',
  }},

  methods: {

    back () {
      this.$emit('update', {section: 'list'})
    },

    crop() {
      this.photo = this.$refs.photosrc.getCroppedCanvas({width: 160}).toDataURL();
    },

    getMember () {
      api('getMember', {
        id: this.member.id
      }).then(
      function(data) {
          this.p = data.member;
          this.photosrc =  this.p.id ? '/members/photo/' + this.p.id + 
            '?time=' + (new Date()).getTime() : 
        '/static/img/nobody.png';
          this.photo = '';
        }.bind(this)
      )
    },

    gotoEdit () {
      this.$emit('update', {section: 'edit', menber: this.member})
    },    

    handleFile(err, file){
      const reader = new FileReader();
      reader.onload = (event) => {
        this.$refs.photosrc.replace(event.target.result);
      };
      reader.readAsDataURL(file.file);
    },
    
    save() {
      api('uploadPhoto', {
        photo: this.photo,
        id: this.p.id,
      }).then(
        function(){
          this.$emit('update', {
            section: 'photo', 
            text: 'Photo saved',
            reload: true,
            member: this.p,
          });
          this.getMember()
        }.bind(this),
        function(err){
          console.log('upload failed', err)
        }
      );
    }

  },

  mounted () {
    this.getMember()
  }

}
</script>

<style>
.dropbox {
  width: 100%;
  height: 100px;
}
.photosrc{
  overflow: hidden;
  width: 100%;
  height: 400px;
  border: 1px dashed #808080;
  background-color: #d3d3d3;
}
.photoresult {
  overflow: hidden;
  position: relative;
  text-align: center;
  width: 160px;
  height: 200px;
}
</style>
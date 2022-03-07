<template>

<v-container>
  <h1>
    <i18n-text
      nl="Pagina niet gevonden"
      fr="Page non trouvée"
      de="Seite nicht gefunden"
      en="Page not found" />
  </h1>
  <p>
    <i18n-text 
      nl="Pagina"
      fr="Page" 
      de="Seite" 
      en="Page" />
    '{{ path }}'
    <i18n-text
      nl="kon niet gevonden worden."
      fr="n'est pas trouvée."
      de="werde nicht gefunden."
      en="was not found." />
  <p>
  <p>
    <i18n-text 
      nl="Als je denkt dat dit een fout is, mag je de webmaster contacteren." 
      fr="Si vous pensez que c'est une erreur, veuillez contacter le webmaster." 
      de="Wenn Sie glauben, dass dies ein Fehler ist, können Sie sich an den Webmaster wenden." 
      en="If you think this is an error, you can contact the webmaster." />
  </p>  
</v-container>

</template>

<script>

import I18nText from "@/components/I18nText"

export default {

  name: 'RouteNotFound',

  data () {return {
    path: this.$route.params.pathMatch
  }},

  components: {
    I18nText,
  }

}
</script>


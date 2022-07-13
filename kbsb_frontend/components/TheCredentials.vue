<template>
  <v-footer app dark class="justify-center green credentials" absolute>
    <div fluid class="d-flex justify-center green darken-2 mt-2 py-2 px-5">
      Website by <a target="_blank" href="https://www.chessdevil.net">
        Chessdevil Consulting</a>. &copy; {{ new Date().getFullYear() }}.
      All rights reserved.
    </div>
  </v-footer>
</template>

<script>

export default {

  name: 'KbsbCredentials'

}

</script>

<style scoped>
.credentials a {
  color: white;
}

.credentials a:link,
.footer a:hover {
  color: white;
  text-decoration: none;
}

.credentials a:hover {
  font-weight: 700;
}
</style>

<template>
    <v-container>
        <p>TO DO</p>
    </v-container>
</template>
<script>

export default {

    name: 'Result',

    data() {
        return {
            club: {},
        }
    },


    computed: {
        logintoken() { return this.$store.state.oldlogin.value },
    },

    methods: {

        emitInterface() {
            this.$emit("interface", "getAnonResult", this.getAnonResult);
        },

        async getAnonResult(activeclub) {
            this.club = activeclub;
        }
    },

    mounted() {
        this.emitInterface();
    },

}
</script>
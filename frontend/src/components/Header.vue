<template>
  <div>
    <v-app-bar
      app
      elevation=1
      color="brown lighten-3"
    >
      <v-btn
        large
        @click="root"
        text
      > Road Network Maker
      </v-btn>
    </v-app-bar>
  </div>
</template>

<script>
export default {

  methods: {
    root: function () {
      this.$router.push('/')
    }
  }

}
</script>

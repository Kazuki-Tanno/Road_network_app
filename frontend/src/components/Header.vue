<template>
  <div>
    <v-app-bar
      app
      elevation=1
      dense
    >
      <v-btn
        @click="root"
        text
      > Road Network Maker
      </v-btn>
    <v-spacer></v-spacer>
      <v-btn
        text
      > How to use
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

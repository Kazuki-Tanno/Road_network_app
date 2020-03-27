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
        @click="dialog = true"
      > How to use
      </v-btn>
    </v-app-bar>

    <v-dialog
      v-model="dialog"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition"
      scrollable
    >
      <v-card tile>
        <v-toolbar
          flat
        >
          <v-btn
            icon
            @click="dialog = false"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>How to use</v-toolbar-title>
            <v-spacer></v-spacer>
          </v-toolbar>
          <v-card-text>
            <v-list
              three-line
              subheader
            >
              <v-subheader>sub header</v-subheader>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Title</v-list-item-title>
                  <v-list-item-subtitle>contents</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Title</v-list-item-title>
                  <v-list-item-subtitle>contents</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
            <v-divider></v-divider>
            <v-list
              three-line
              subheader
            >
              <v-subheader>sub header</v-subheader>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Title</v-list-item-title>
                  <v-list-item-subtitle>contents</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Title</v-list-item-title>
                  <v-list-item-subtitle>contents</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card-text>

          <div style="flex: 1 1 auto;"></div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  name:'header',

  data(){
    return {
      dialog: false
    }
  },

  methods: {
    root: function () {
      this.$router.push('/')
    }
  }

}
</script>

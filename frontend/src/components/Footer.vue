<template>
<div>
<v-footer
  absolute
  padless
  height="40"
>
  <div>
    <span class="font-weight-light">&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | </span>
    <span class="font-weight-light caption">Contains information from Road Network Maker, which is made available
    here under the <a href="https://opendatacommons.org/licenses/odbl/1.0/">Open Data Licese (ODbL)</a></span>
  </div>
  <v-spacer></v-spacer>
    <div>
      <span class="font-weight-regular">{{ new Date().getFullYear() }} - </span>
      <span class="font-weight-light">Kazuki Tanno</span>
    </div>
</v-footer>
</div>
</template>

<script>
export default {

  methods: {}

}
</script>

<template>
<div>
  this is map.vue
  <br>
  <div id="map" style="width:100%; height:600px"></div>
</div>
</template>

<script>
//import axios from 'axios'
import L from "leaflet"

export default {
  name: 'HomePage',

  // データプロパティ
  data () {
    return {
      // 入力データ
      shop_info: null,
      map: null
    }
  },

  // ライフサイクルフック関数
  created () {},

  // 算術プロパティ
  computed: {},

  // 監視プロパティ
  watch: {},

  mounted () {
      // mapオブジェクトを作成
      this.map = L.map('map', { center: L.latLng( 35.6825, 139.752778 ), zoom: 15 } ).addLayer(
        L.tileLayer( 'http://{s}.tile.osm.org/{z}/{x}/{y}.png' )
    )
  },

  // メソッドプロパティ
  methods: {

    // 地図の表示位置を移動
  }
}
</script>

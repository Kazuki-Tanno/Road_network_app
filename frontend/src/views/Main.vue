<template>

<v-container fluid>
<v-row no-gutters>
  <!-- geojson生成ページ -->
  <v-col cols="6">
    <v-row no-gutters>
    <v-col cols="12">
      <!-- タブ -->
      <v-tabs v-model="tabs" color="primary" dark>
        <v-tab> Mapから生成 </v-tab>
        <v-tab> Geojsonファイルから生成 </v-tab>
      </v-tabs>

      <!-- タブの中身 -->

        <!-- Mapタブ -->

          <v-row no-gutters>


          <!-- Map部分 -->
          <v-col cols="9">
            
            <div id="map" style="width:100%; height:500px"></div>

          </v-col>


          <!-- 検索部分 -->
          <v-col cols="3">
            <v-row no-gutters align="baseline">
            <v-col cols="10">
              <v-text-field
                v-model="SearchString"
                label="検索ワード"
                required
              ></v-text-field>
            </v-col>
            <v-col cols="2">
              <v-btn @click="SearchSpot" icon><v-icon>mdi-magnify</v-icon></v-btn>
            </v-col>
            </v-row>

            <!-- 検索結果表示 -->
            <v-list :two-line="true" dense>
              <v-list-item-group>
                <v-list-item
                  v-for="(item, id) in SpotList"
                  :key="item.id"
                  @click="PanMap(GetLatLon(id))"
                >
                  <v-list-item-content class="pa-0">
                    <v-list-item-title v-text="item['properties']['title']"></v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list-item-group>
            </v-list>

          </v-col>
          </v-row>


        <!-- ファイル入力タブ -->

          tab2

    </v-col>
    </v-row>

    <v-row>
      <v-col>アイテム</v-col>
    </v-row>
  </v-col>

  <v-col cols="6">colB</v-col>

</v-row>
</v-container>
</template>

<script>
import axios from 'axios'
import L from "leaflet"

export default {
  name: 'MainPage',

  // データプロパティ
  data () {
    return {
      // タブのステータス
      tabs: null,
      // map要素
      map: null,
      ExportItems: null,
			Status: 0,
      // 地名検索
      SpotList: null,
			SearchString: '',
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
      L.tileLayer( 'http://{s}.tile.osm.org/{z}/{x}/{y}.png' ));
      
    // 描画レイヤの初期化
    var drawnItems = new L.FeatureGroup().addTo(this.map);
    var drawControl = new L.Control.Draw({
      draw: {
        circle: false,
        polyline: false,
        marker: false
      },
      edit: {
        featureGroup: drawnItems,
      },
    }).addTo(this.map);

    // 描画した図形を地図上にそのまま表示
    this.map.on('draw:created', function(e) {
      drawnItems.addLayer(e.layer);
    });

    this.ExportItems = drawnItems
  },

  methods: {
    // 地名検索
    SearchSpot : function(){

      // クエリ用の文字列を生成
      var QueryString = 'https://msearch.gsi.go.jp/address-search/AddressSearch?q=' + this.SearchString;

      axios
      .get(QueryString)
      .then(response => {
          this.SpotList=response.data;
          //console.log(this.SpotList)
          })
      .catch(err => {
          alert('APIサーバと接続できません');
          //print(err)
      });
    },
    
    // クリックした検索結果の緯度経度を取得する関数
		GetLatLon: function(id){
			return this.SpotList[id]['geometry']['coordinates']
		},

		// 指定した緯度経度に地図を移動
    PanMap: function(LatLon){
			this.map.panTo(new L.LatLng(LatLon[1], LatLon[0]))
		},
  }
}
</script>

<style>
.v-list{
  height:500px;/* or any height you want */
	overflow-y:auto;
}
</style>

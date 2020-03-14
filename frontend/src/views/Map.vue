<template>
<div>
  <v-text-field
    v-model="SearchString"
    label="検索ワード"
    required
  ></v-text-field>
	<v-btn @click="SearchSpot">検索</v-btn>
  <v-list
    :two-line="true"
		dense
  >
    <v-list-item-group color="blown">
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
  <br>
  <div id="map" style="width:100%; height:600px"></div>
	<v-btn @click="MakeGeoJson">Geojson</v-btn>
</div>
</template>

<script>
import axios from 'axios'
import L from "leaflet"

export default {
  name: 'HomePage',

  // データプロパティ
  data () {
    return {
      // 入力データ
      map: null,
      SpotList: null,
			SearchString: '',
			ExportItems: null
    }
  },

  // ライフサイクルフック関数
  created () {},

  // 算術プロパティ
  computed: {},

  // 監視プロパティ
  watch: {},

  mounted: function() {
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

  // メソッドプロパティ
  methods: {
    // 地名検索+リストで表示
    SearchSpot : function(){

        // クエリ用の文字列を生成
        var QueryString = 'https://msearch.gsi.go.jp/address-search/AddressSearch?q=' + this.SearchString;

        axios
        .get(QueryString)
        .then(response => {
            this.SpotList=response.data;
            console.log(this.SpotList)
            })
        .catch(err => {
            alert('APIサーバと接続できません');
            print(err)
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
		
		//geojson化
		MakeGeoJson: function(){
			
			var return_data = this.ExportItems.toGeoJSON()
			if (return_data['features'].length > 0) {
				console.log(return_data)
				axios
				.post('/api/post', return_data)
        .then(response => {
          console.log(response.data)
        })
        .catch(err => {
          alert('APIサーバと接続できません')
        })
			}
			else{
				alert('geojsonを作成してください')
			}
		}
  }
}
</script>

<style>
.v-list{
  height:400px;/* or any height you want */
	overflow-y:auto;
}
</style>
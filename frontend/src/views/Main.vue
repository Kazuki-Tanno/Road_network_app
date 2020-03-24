<template>

<v-container fluid>
<v-row dense>
<!-- geojson生成列 -->
<v-col cols="6">

  <!-- 多角形描画部分 -->
  <v-row dense>
    <!-- Map部分 -->
    <v-col cols="9">
      <v-card
      class="mx-auto"
      outlined
      height="600"
      >
        <div id="map" style="width:100%; height:100%"></div>
      </v-card>
    </v-col>

    <!-- 検索部分 -->
    <v-col cols="3" class="pa-0">
      <v-card outlined>
        <!-- 入力部分 -->
        <v-row dense align="baseline" justify="start">
          <v-col cols="8" class="ml-2 pa-0">
            <v-text-field
            v-model="SearchString"
            label="地名"
            required
            class="pt-3"
            outlined
            dense></v-text-field>
          </v-col>
          <v-col cols="2">
            <v-btn @click="SearchSpot" fab x-small outlined><v-icon>mdi-magnify</v-icon></v-btn>
          </v-col>
        </v-row>

        <!-- 結果表示部分 -->
        <v-list dense>
          <v-list-item-group>
            <v-list-item
            v-for="(item, id) in SpotList"
            :key="item.id"
            @click="PanMap(GetLatLon(id))"
            >

            <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-list-item-content class="pa-0" v-on="on">
                <v-list-item-title v-text="item['properties']['title']"></v-list-item-title>
              </v-list-item-content>
            </template>
            <span>{{item['properties']['title']}}へ移動</span>
            </v-tooltip>

            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-card>
    </v-col>
  </v-row>

  <v-divider></v-divider>

  <!-- 出力ボタン部分 -->
  <v-row no-gutters align="center" justify="start">
    <!-- ネットワークのタイプ -->
    <v-col cols="3" align-self="start">
      <v-subheader class="pa-0">道路網のタイプを指定</v-subheader>
      <v-select
      v-model="NetworkType"
      :items="NetworkTypeList"
      label="Network Type"
      class="pt-2 ma-0"
      ></v-select>
    </v-col>

    <v-divider class="mx-2" vertical inset></v-divider>

    <!-- 簡略化の比率 -->
    <v-col cols="4" align-self="start">
      <v-subheader class="pa-0">ネットワークの簡略化度を指定</v-subheader>
      <v-slider
      v-model="SimplifyRate"
      class="pt-2"
      dense
      max=180
      min=0
      hint="0~180の数値を指定"
      persistent-hint
      :thumb-size="21"
      thumb-label="always"
      >
      </v-slider>
    </v-col>

    <v-divider class="mx-2" vertical inset></v-divider>

    <!-- 枝ノード削除 -->
    <v-col cols="3" class="px-0">
      <v-checkbox
      v-model="DeleteOneNode"
      :true-value="1"
      :false-value="0"
      dense
      label="末端ノード削除"
      persistent-hint
      hint="次数が1のノードを削除する"></v-checkbox>
    </v-col>

    <v-divider class="mx-2" vertical inset></v-divider>

    <!-- ネットワーク作成ボタン -->
    <v-col cols="1">
      <v-btn @click="MakeGeoJson" outlined max-width="70"> 生成 </v-btn>
    </v-col>
  </v-row>
</v-col>

<!-- ネットワーク編集列 -->
<v-col cols="6">
{{ RoadNetwork }}
<br>
{{ DeleteOneNode }}
</v-col>

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
      tabs: 0,
      // map要素
      map: null,
      ExportItems: null,
      Status: 0,
      // ネットワークの出力オプション
      NetworkType: 'drive',
      NetworkTypeList: ['drive', 'walk', 'bike', 'drive_service', 'all', 'all_private'],
      SimplifyRate: 180,
      DeleteOneNode: 1,
      rules: {rate: value => {
          var IsOK = false;
          if (typeof(value)=='number' && 0 <= value && value <= 180) {
            IsOK = true;
          }
          return IsOK || 'Invalid number';
        }
      },
      // 地名検索
      SpotList: null,
      SearchString: '',
      // ネットワークデータ
      RoadNetwork: null
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
          this.SpotList=response.data.slice(0, 21);
          })
      .catch(err => {
          alert('APIサーバと接続できません');
      });
    },
    
    // クリックした検索結果の緯度経度を取得する関数
		GetLatLon: function(id){
			return this.SpotList[id]['geometry']['coordinates'];
		},

		// 指定した緯度経度に地図を移動
    PanMap: function(LatLon){
			this.map.panTo(new L.LatLng(LatLon[1], LatLon[0]));
    },

    //geojson化
		MakeGeoJson: function(){
			var return_data = {
        'GeoJson':this.ExportItems.toGeoJSON(),
        'NetworkType':this.NetworkType,
        'SimplifyRate':this.SimplifyRate,
        'DeleteOneNode':this.DeleteOneNode
      };
			if (return_data['GeoJson']['features'].length > 0) {

				axios
				.post('/api/post_geojson', return_data)
        .then(response => {
					this.Status = response.data['Status'];

					// storeのデータを上書き
          this.$store.dispatch('UpdateNetwork', response.data['Network']);
          this.RoadNetwork = response.data['Network'];
				
        })
        .catch(err => {
          alert('APIサーバと接続できません');
        });
			}
			else{
				alert('geojsonを作成してください');
			}
		}
  }
}
</script>

<style>
.v-list{
  height:520px;
	overflow-y:auto;
}
#map {
  z-index: 1;
}
</style>

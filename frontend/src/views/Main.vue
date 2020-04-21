<template>

<v-container fluid>
<v-row dense>
<!-- geojson生成列 -->
<v-col cols="7">

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
<v-col cols="5">

  <!-- 編集パレット -->
  <v-row no-gutters justify="start">
    <v-col>
      <v-btn-toggle
      v-model="Palette"
      dense
      background-color="primary"
      dark
      >
        <v-btn value="AddNode" @click="ResetPaletteSub">
          <span class="hidden-sm-and-down">Add Node</span>
          <v-icon right>mdi-plus-circle</v-icon>
        </v-btn>

        <v-btn value="DeleteNode" @click="ResetPaletteSub">
          <span class="hidden-sm-and-down">Delete Node</span>
          <v-icon right>mdi-minus-circle</v-icon>
        </v-btn>

        <v-btn value="AddEdge" >
          <span class="hidden-sm-and-down">Add Edge</span>
          <v-icon right>mdi-vector-polyline-plus</v-icon>
        </v-btn>

        <v-btn value="DeleteEdge" @click="ResetPaletteSub">
          <span class="hidden-sm-and-down">Delete Edge</span>
          <v-icon right>mdi-vector-polyline-minus</v-icon>
        </v-btn>
      </v-btn-toggle>
    </v-col>
  </v-row>

<!-- 編集ゾーン -->
  <v-row no-gutters justify="start">
    <v-col cols="5">
      <v-slider
      v-model="NodeSize"
      class="pa-0"
      dense
      max=50
      min=0
      hint="Node Size"
      persistent-hint
      >
      </v-slider>
    </v-col>
    <v-divider class="mx-2" vertical inset></v-divider>
    <v-col cols="5">
      <v-slider
      v-model="EdgeWidth"
      class="pa-0"
      dense
      max=25
      min=0
      hint="Edge Width"
      persistent-hint
      >
      </v-slider>
    </v-col>
  </v-row>

  <!-- 編集ウィンドウ -->
  <v-row dense>
    <!-- 編集画面 -->
    <v-col cols="12">
    <v-card class="mx-auto" outlined>
      <svg width="100%" :height="Height" :style="SvgStyle" class="Network" :viewBox="viewBox">
        <g class="Network" ></g>
      </svg>
    </v-card>
    </v-col>
  </v-row>

  <!-- 出力ボタン -->
  <v-row dense justify="end">
  <v-col cols="3">
    <v-btn @click="SaveFile" outlined>CSVで保存</v-btn>
  </v-col>
  </v-row>

</v-col>
</v-row>

<!-- overlay -->
<v-overlay :value="overlay">
  <v-progress-circular indeterminate size="64"></v-progress-circular>
</v-overlay>

</v-container>
</template>

<script>
import axios from 'axios';
import L from 'leaflet';
import * as d3 from 'd3';
import saveAs from 'file-saver';
import JSZip from 'jszip';

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
      RoadNetwork: {node:[], edge:[]},
      // 編集モードの選択状況
      Palette: null,
      PaletteSub: null,
      NowTargetNode: null,
      // svgの設定
      Height: 510,
      SvgStyle: "background-color: #ffffff",
      Transform: {x:0, y:0, k:1},
      NodeSize: 8,
      EdgeWidth: 2,
      // ローディング変数
      overlay: false
    }
  },

  // ライフサイクルフック関数
  created () {
    this.SetESCKey();
  },

  // 算術プロパティ
  computed: {
    // viewBox要素を常に計算する
		viewBox:function(){
			return '0 0 ' + this.Height + ' ' + this.Height;
    }
  },

  // 監視プロパティ
  watch: {
    Palette: function (val) {
      if (val!=="AddEdge"){
				this.PaletteSub = null;
				this.NowTargetNode = null;
			}
    },
    NodeSize: function (val) {
			if (val < 0) {
        this.NodeSize = 0;
        val = 0;
			}
			// 変更する部分だけ書き直せば良い
			const node = d3.select("g.node");
			node.selectAll("circle").data(this.RoadNetwork.node).attr("r", val).attr("stroke-width", val/6);
    },
    EdgeWidth: function (val) {
      if(val < 0) {
        this.EdgeWidth = 0;
        val = 0;
      }
      const edge = d3.select("g.edge");
			edge.selectAll("line").data(this.RoadNetwork.edge).attr("stroke-width", val);
    }
  },

  mounted () {
    // map要素を初期化
    this.MapInit();

    // D3の初期化
    this.InitD3();
    
  },

  methods: {

    /* Map関連 */
    // 地図の初期化
    MapInit: function(){
      // mapオブジェクトを作成
      this.map = L.map('map', { center: L.latLng( 35.6825, 139.752778 ), zoom: 15 } ).addLayer(
      L.tileLayer( 'http://{s}.tile.osm.org/{z}/{x}/{y}.png',{
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
} ));
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

      this.ExportItems = drawnItems;
    },

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
			if (return_data['GeoJson']['features'].length === 1) {
        
        // ローディング画面
        this.overlay = true;

				axios
				.post('/api/post_geojson', return_data)
        .then(response => {
					this.Status = response.data['Status'];

					// storeのデータを上書き
          this.$store.dispatch('UpdateNetwork', response.data['Network']);
          this.RoadNetwork = response.data['Network'];
          d3.select("g.Network").selectAll("*").remove();
          this.InitEdge();
          this.InitNode();
          this.overlay = false;
        })
        .catch(err => {
          this.overlay = false;
          alert('APIサーバと接続できません');
        });
			}
			else if(return_data['GeoJson']['features'].length === 0){
				alert('geojsonを作成してください');
			}else{
        alert('複数の多角形が作成されています (作成する多角形は1つのみにしてください)')
      }
    },
    
    /* Edit関連 */
    // ESCキーの挙動を設定
    SetESCKey: function(){
      var me = this;
      document.addEventListener('keydown', (event) => {
        if (event.key=="Escape") {
          if (me.PaletteSub=="SearchNode"){
            me.Palette="AddEdge";
            me.NowTargetNode=null;
            me.PaletteSub=null;
            d3.select("line.cursorLine")
              .attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 0);
          }
          else{
            me.NowTargetNode=null;
            me.PaletteSub=null;
            me.Palette=null;
            d3.select("circle.cursorCircle").attr("r",0);
          }
        } 
      });
    },

    // PaletteSubをリセット
    ResetPaletteSub: function(){
			this.PaletteSub = null;
			this.NowTargetNode = null;
    },
    
    // D3の初期化
    InitD3: function(){

      var me = this;
      this.RoadNetwork = this.$store.state.Network;

      me.InitEdge();
      me.InitNode();

      d3.select("svg.Network").attr("cursor", "all-scroll");

      // AddNodeモードで表示するカーソル
      d3.select("svg.Network")
        .append("circle")
        .attr("class","cursorCircle")
        .attr("cx",0).attr("cy",0).attr("r",0)
        .attr("fill","black")
        .attr("fill-opacity", 0.7);

      d3.select("svg.Network")
        .append("line")
        .attr("class","cursorLine")
        .attr("x1",0).attr("y1",0).attr("x2",0).attr("y2",0)
        .attr("stroke-dasharray", "5,5")
        .attr("stroke", "black")
        .attr("stroke-opacity", 0.5)
        .attr("stroke-width", 4);

      // zoomのイベント・リスナーを追加
      d3.select("svg.Network").call(d3.zoom()
        .extent([[0, 0], [me.Height, me.Height]])
        .scaleExtent([0, 1000])
        .on("zoom", me.zoomed));

      // svg全体のクリック時イベント・リスナーを追加
      d3.select("svg.Network")
        .on("click", function(){

          if (me.Palette=="AddNode") { // AddNodeモードの場合, クリックした位置にノードを追加する

          var tl = [me.Transform.x, me.Transform.y];
          var sc = me.Transform.k;
          var MousePos = [(d3.mouse(this)[0] - tl[0])/sc, (d3.mouse(this)[1] - tl[1])/sc];
          // クリック位置のy座標を反転
          MousePos[1] = me.NodeYPos(MousePos[1]);

          // データにプッシュ
          // idは現配列に格納されているidの最大値+1
          var id = 0;
          if (me.RoadNetwork.node.length!==0){
            id = me.RoadNetwork.node.reduce((a,b)=>a.id>b.id?a:b).id + 1;
          }
          var add_data = {"id":id, "pos":MousePos};
          me.RoadNetwork.node.push(add_data);

          // nodeを追加
          var g = d3.select("g.node");
          me.AddNode(g);
          }
        })
      .on("mousemove", function(){
        var tl = [me.Transform.x, me.Transform.y];
        var sc = me.Transform.k;

        if (me.PaletteSub==="SearchNode") {
          var pre_select = me.GetNodePos(me.RoadNetwork.node, me.NowTargetNode)
          d3.select("line.cursorLine")
            .attr("x1", (pre_select[0]*sc)+tl[0])
            .attr("y1", (me.YPos(pre_select[1])*sc+tl[1]))
            .attr("x2", d3.mouse(this)[0])
            .attr("y2", d3.mouse(this)[1]);
        } else if (me.Palette==="AddNode") {
          d3.select("circle.cursorCircle")
          .attr("cx",d3.mouse(this)[0]).attr("cy",d3.mouse(this)[1]).attr("r",5);
        } else {
          true
        }

        if (me.Palette===null){
          d3.select("svg.Network").attr("cursor", "all-scroll");
        }else{
          d3.select("svg.Network").attr("cursor", "crosshair");
        }
      })
      .on("mouseout", function(){
        d3.select("line.cursorLine")
          .attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 0);
        d3.select("circle.cursorCircle").attr("r",0);
      });
    },

    // ネットワーク系
		// zoom関数
		zoomed: function() {
			var me = this
			me.Transform = d3.event.transform;
			d3.select("g.Network").attr("transform", d3.event.transform);
		},

		// node_idのノードのposを返す関数
		GetNodePos: function(node_list, node_id){
			var pos = node_list.filter( function(v){
				if (Number(node_id) == v.id){ return v.pos }
			} )[0].pos

			return pos
		},

		// yのposを反転して返すメソッド
		YPos: function(v){ return this.Height - v },

		// 画面の位置からYposを返す関数
		NodeYPos: function(v){ return this.Height - v; },

		// 常に追加してあるエッジか否かを判定する関数
		CanAddEdge: function(v, h){
			var result = true;
			if(v===h){
				result = false;
			}else{
				var me = this;
				var edge_list = [];
				me.RoadNetwork.edge.forEach(element => {
					if (element.head===v ) { edge_list.push(element.tail)}
					else if ( element.tail===v ) { edge_list.push(element.head)}
				});
				// 重複削除
				edge_list = edge_list.filter(function (x, i, self) {
					return self.indexOf(x) === i;
				});

				// 追加可能なエッジか判別
				result = true;
				edge_list.forEach(element => {
					if (element===h) { result = false;}
				});
      }
      
			return result
    },

    // ノードを追加するメソッド(クリック時の挙動も定義するので関数化する)
		AddNode: function(g){
			var me = this;

			g.selectAll("circle").data(me.RoadNetwork.node, function(d){return d.id;}).enter().append("circle")
				.attr("cx", ({pos}) => pos[0]).attr("cy", ({pos}) => me.YPos(pos[1]))
        .attr("r", me.NodeSize)
        .attr("fill", "white")
        .attr("fill-opacity", 1)
        .attr("stroke-width", me.NodeSize/5)
        .attr("stroke", "gray")
				.on("click",function(d){

					if (me.Palette=="AddEdge"){ // edgeを追加しているとき
						if (me.PaletteSub=="SearchNode") { // tailノードを探しているとき
							if (me.CanAddEdge(me.NowTargetNode, d.id)) { // もしedgeをちゃんと追加できるなら

								var id = 0;
								if(me.RoadNetwork.edge.length!==0){
                  id = me.RoadNetwork.edge.reduce((a,b)=>a.id>b.id?a:b).id + 1;
								}
								var add_data = {"id":id, "head":me.NowTargetNode, "tail":d.id}
								me.RoadNetwork.edge.push(add_data)

								// エッジを追加
								me.AddEdge(d3.select("g.edge"))

								d3.select("line.cursorLine")
									.attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 0);

								me.PaletteSub = null;
								me.NowTargetNode = null;
							}
						} else {
							me.NowTargetNode = d.id
							me.PaletteSub = "SearchNode";
						}
						
					} else if (me.Palette=="DeleteNode"){ // ノード削除モードのとき

						// ノードを削除
						me.DeleteNode(g, d.id);

						// 隣接したエッジを削除
						// 削除するエッジのidのリストを作成
						var delete_list = []
						me.RoadNetwork.edge.forEach(element => {
							if (element.head===d.id || element.tail===d.id ) {
								delete_list.push(element.id)
							}
            });

						delete_list = delete_list.filter(function (x, i, self) {
							return self.indexOf(x) === i;
						});
						var edge_g = d3.select("g.edge")
						delete_list.forEach(element => { me.DeleteEdge(edge_g, element) });

					}
				})
				.on("mouseover", function(){
					d3.select(this).attr("stroke", 'royalblue');
				})
				.on("mouseout", function(){
					d3.select(this).attr("stroke", "gray");
				});
		},

		AddEdge: function(g){
			var me = this;

			g.selectAll("line")
				.data(me.RoadNetwork.edge, function(d){return d.id}).enter()
				.append("line")
				.attr("x1", function(d){return me.GetNodePos(me.RoadNetwork.node, d.head)[0]})
				.attr("y1", function(d){return me.YPos(me.GetNodePos(me.RoadNetwork.node, d.head)[1])})
				.attr("x2", function(d){return me.GetNodePos(me.RoadNetwork.node, d.tail)[0]})
				.attr("y2", function(d){return me.YPos(me.GetNodePos(me.RoadNetwork.node, d.tail)[1])})
				.attr("stroke-width", me.EdgeWidth)
        .attr("stroke", "black")
        .attr("stroke-opacity", 0.6)
				.on("click",function(d){
					if (me.Palette==="DeleteEdge"){
						me.DeleteEdge(g, d.id)
					}
				})
				.on("mouseover", function(){
					d3.select(this).attr("stroke", "royalblue");
				})
				.on("mouseout", function(){
					d3.select(this).attr("stroke", "black");
				});

		},

		// ノードを削除するメソッド
		DeleteNode: function(g, node_id){// node_idは削除するノードのid
			var me = this;
			// nodeリストから削除
			me.RoadNetwork.node = me.RoadNetwork.node.filter( function(item){ return item.id!==node_id; } );
			// 消されたリストを反映
			// data部分はidで設定しないと上手く消せない
			g.selectAll("circle").data(me.RoadNetwork.node, function(d){return d.id;}).exit().remove();
		},

		// エッジを削除するメソッド
		DeleteEdge: function(g, edge_id){
			var me = this;
			// edgeリストから削除
			me.RoadNetwork.edge = me.RoadNetwork.edge.filter( function(item){ return item.id!==edge_id; } );
			// 消されたリストを反映
			g.selectAll("line").data(me.RoadNetwork.edge, function(d){ return d.id; }).exit().remove();
		},

		InitEdge: function(){

			// d3のfunction内でthisに指定する関数は使えない模様
			var me = this
			// svgのグループを作成
			var g = d3.select("g.Network")
			const edge = g.append("g").attr("class", "edge")
			// edgeを描画
			me.AddEdge(edge)
		},

		InitNode:function(){

			var me = this;
			// svgを検索
			var svg = d3.select("g.Network");
			// svgのグループを作成
			const g = svg.append("g").attr("class", "node");
			me.AddNode(g);
		},
    
    // CSVの保存
		SaveFile: function(){

			// ノードcsvを作成
			// column行
			var node_csv = "id, x, y \n";
			var node_id = 0

			this.RoadNetwork.node.forEach(element => {
				node_csv += `${String(node_id)},${String(element.pos[0])},${String(element.pos[1])}\n`;
				node_id += 1;
			});

			// エッジcsv
			var edge_csv = "";
			this.RoadNetwork.edge.forEach(element => {
				edge_csv += `${String(element.head)},${String(element.tail)}\n`
			});

			var zip = new JSZip();
			zip.file("node.csv", node_csv);
			zip.file("edge.csv", edge_csv);
			zip.generateAsync({type:"blob"})
				.then(function(content) {
					// see FileSaver.js
					saveAs(content, "road_network.zip");
				});
		},
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

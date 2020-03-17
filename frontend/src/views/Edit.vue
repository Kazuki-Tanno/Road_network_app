<template>
<div>
  this is edit.vue<br>
	<v-btn @click="BiggerNode(1)">BiggerNode</v-btn>
	<v-btn @click="BiggerNode(-1)">SmollerNode</v-btn>
	<v-btn @click="ChangeSVG(10)">SVG拡大</v-btn>
	<v-btn @click="ChangeSVG(-10)">SVG縮小</v-btn>
	<br><br>

	<!-- パレットボタン -->
	<v-btn-toggle
		v-model="palette"
		dense
		background-color="primary"
		dark
	>
		<v-btn value="AddNode">
			<span class="hidden-sm-and-down">Add Node</span>
      <v-icon right>mdi-plus-circle</v-icon>
		</v-btn>

		<v-btn value="DeleteNode" >
			<span class="hidden-sm-and-down">Delete Node</span>
      <v-icon right>mdi-minus-circle</v-icon>
		</v-btn>

		<v-btn value="AddEdge" >
			<span class="hidden-sm-and-down">Add Edge</span>
      <v-icon right>mdi-vector-polyline-plus</v-icon>
		</v-btn>

		<v-btn value="DeleteEdge">
			<span class="hidden-sm-and-down">Delete Edge</span>
      <v-icon right>mdi-vector-polyline-minus</v-icon>
		</v-btn>
	</v-btn-toggle>

	{{ palette }}
	<br>

	<svg :width="width" :height="height" :viewBox="viewBox"
	:style="style" class="Network">
	<g class="Network" ></g>
	</svg>
	<br>
</div>
</template>

<script>
import axios from 'axios'
import * as d3 from 'd3'

export default {
  name: 'EditPage',

  // データプロパティ
  data () {
    return {
			// svg要素の初期化用
			height: 500,
			width: 500,
			style: "background-color: #ededed",
			transform: {x:0, y:0, k:1},

			// パレット
			palette: null,

			// 入力データ
			// ノードサイズ
			node_size: 10,
			// D3用のテストデータ
      test_network: {
        node: [
					{id:0, pos:[0,0], latlon:[4,5]},
					{id:1, pos:[200,0], latlon:[3,5]},
					{id:2, pos:[0,200], latlon:[4,2]},
					{id:3, pos:[200,200], latlon:[1,3]},
					{id:4, pos:[100,50], latlon:[4,5]}
        ],
				edge: [[0,1],[0,2],[1,3],[2,3],[0,4],[1,4]]
			}
    }
  },

  // ライフサイクルフック関数
  created () {
		// escapeキーの挙動を設定
		// vueのthisのスコープ範囲をケアして，代入しておく
		var me = this
		document.addEventListener('keydown', (event) => {
			if (event.key=="Escape") {
				if (me.palette=="SearchNode"){ me.palette="AddEdge"; }
				else{ me.palette=null; }
			} 
		});
	},

  // 算術プロパティ
  computed: {
		// viewBox要素を常に計算する
		viewBox:function(){
			return '0 0 ' + this.width + ' ' + this.height;
    }
	},

  // 監視プロパティ
  watch: {},

  mounted () {
		//this.test_network = this.$store.state.Network

		this.AddEdge();
		this.AddNode();

		// zoomのイベント・リスナーを追加
		d3.select("svg.Network").call(d3.zoom()
      .extent([[0, 0], [this.width, this.height]])
      .scaleExtent([0, 1000])
			.on("zoom", this.zoomed));

		// vueのthisのスコープ範囲がおそらくd3の中身に及ばなさそう
		var me = this;

		// クリック時のイベント・リスナーを追加
		d3.select("svg.Network").on("click", function(){
			
			// クリック時のposを取得
			//var MousePos = d3.mouse(this)
			var tl = [me.transform.x, me.transform.y]
			var sc = me.transform.k
			var MousePos = [(d3.mouse(this)[0] - tl[0])/sc, (d3.mouse(this)[1] - tl[1])/sc]
			MousePos[1] = me.NodeYPos(MousePos[1])
			// nodeデータに追加
			var add_data = {"id":9, "pos":MousePos}
			me.test_network.node.push(add_data)

			// グループ要素を見つける
			var g = d3.select("g.node")
			g.selectAll("circle").data(me.test_network.node).enter().append("circle")
			.attr("cx", ({pos}) => pos[0]).attr("cy", ({pos}) => me.YPos(pos[1]))
			.attr("r", me.node_size)
		});
	},
	
  methods: {
		// zoom関数
		zoomed: function() {
			this.transform = d3.event.transform;
			d3.select("g.Network").attr("transform", d3.event.transform);
		},

		ChangeSVG: function(n){
				this.height += n
				this.width += n
			},

		BiggerNode: function(n){
			this.node_size += n
			if (this.node_size < 0) {
				this.node_size = 0
			}
			// 変更する部分だけ書き直せば良い
			const node = d3.select("g.node")
			node.selectAll("circle").data(this.test_network.node).attr("r", this.node_size)
		},

		// node_idのノードのposを返す関数
		GetNodePos: function(node_list, node_id){
			
			var pos = node_list.filter( function(v){
				if (Number(node_id) == v.id){ return v.pos }
			} )[0].pos

			return pos
		},

		// yのposを反転して返すメソッド
		YPos: function(v){
			return this.height - v
		},

		// 画面の位置からYposを返す関数
		NodeYPos: function(v){
			return this.height - v
		},

		AddEdge: function(){
			
			var g = d3.select("g.Network")

			// svgのグループを作成
			const edge = g.append("g").attr("class", "edge")

			// d3のfunction内でthisに指定する関数は使えない模様
			var me = this

			// edgeを描画
			edge.selectAll("line")
				.data(me.test_network.edge).enter()
				.append("line")
				.attr("style", "stroke:#000;stroke-width:5")
				.attr("x1", function(d){return me.GetNodePos(me.test_network.node, d[0])[0]})
				.attr("y1", function(d){return me.YPos(me.GetNodePos(me.test_network.node, d[0])[1])})
				.attr("x2", function(d){return me.GetNodePos(me.test_network.node, d[1])[0]})
				.attr("y2", function(d){return me.YPos(me.GetNodePos(me.test_network.node, d[1])[1])})
				.on("click",function(d,idx,elem){
					var msg = "data:" + d + " idx:" + idx + " elem:" + elem + " d3.event.pageX: " + d3.event.pageX + " d3.mouse: " + d3.mouse(this) ;
					alert(msg);
				});
		},

		AddNode:function(){
			
			// svgを検索
			var svg = d3.select("g.Network")
			var YPos = this.YPos

			// svgのグループを作成
			const node = svg.append("g").attr("class", "node")

			// nodeを描画
			node.selectAll("circle")
        .data(this.test_network.node)
        .enter()
        .append("circle").attr("cx", ({pos}) => pos[0]).attr("cy", ({pos}) => YPos(pos[1]))
        .attr("r", this.node_size).attr("fill", "#000000")
				// クリックイベントの追加
				.on("click",function(d,idx,elem){
					var msg = "data:" + d.pos + " idx:" + idx + " elem:" + elem + " d3.event.pageX: " + d3.event.pageX + " d3.mouse: " + d3.mouse(this) ;
					alert(msg);
				});

			/*
			// テキストを表示
			const text = svg.append("g")

			// テキストを描画
			text.selectAll("text")
				.data(this.test_network.node)
				.enter()
				.append("text").text( 
					function(d){ return d.id + ": [" + String(d.pos) + "]" }
				)
				.attr("x", ({pos}) => pos[0]).attr("y", ({pos}) => YPos(pos[1]))
				.attr("font-family", "sans-serif").attr("font-size", "10px")
				.attr("text-anchor", "middle").attr("dominant-baseline", "central")
				.attr("fill", "white");
				*/
		}
	}
}
</script>

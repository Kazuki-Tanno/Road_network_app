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
	{{ palette }} / {{ palette_sub }} /{{ now_target_node }}/
	{{ transform.x }}/{{ transform.y }}/{{ transform.k }}
	<br>

	<svg :width="width" :height="height" :viewBox="viewBox"
	:style="style" class="Network">
	<g class="Network" ></g>
	</svg>
	<br>
	{{ test_network.node }}
	<br>
	{{ test_network.edge }}
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

			// パレットの選択状態
			palette: null,
			// パレットの選択のサブ状態
			palette_sub: null,

			// AddEdgeで選択されているノード
			now_target_node: null,

			// 入力データ
			// ノードサイズ
			node_size: 10,
			// D3用のテストデータ
      test_network: {
        node: [
					{id:0, pos:[0,0]},
					{id:1, pos:[200,0]},
					{id:2, pos:[0,200]},
					{id:3, pos:[200,200]},
					{id:4, pos:[100,50]}
        ],
				edge: [
					{id:0, head:0, tail:1},
					{id:1, head:0, tail:2},
					{id:2, head:1, tail:3},
					{id:3, head:2, tail:3},
					{id:4, head:0, tail:4},
					{id:5, head:1, tail:4}
				]
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
				if (me.palette_sub=="SearchNode"){
					me.palette="AddEdge";
					me.now_target_node=null;
					me.palette_sub=null;
					d3.select("line.cursorLine")
						.attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 0);
				}
				else{
					me.now_target_node=null;
					me.palette_sub=null;
					me.palette=null;
					d3.select("circle.cursorCircle").attr("r",0);
				}
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
  watch: {
		palette: function (val) {
      if (val!=="AddEdge"){
				this.palette_sub = null;
				this.now_target_node = null;
			}
    },
	},

  mounted () {
		// vueのthisのスコープ範囲の問題を解消
		var me = this;

		//this.test_network = this.$store.state.Network

		me.InitEdge();
		me.InitNode();

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
      .extent([[0, 0], [me.width, me.height]])
      .scaleExtent([0, 1000])
			.on("zoom", me.zoomed));

		// svg全体のクリック時イベント・リスナーを追加
		d3.select("svg.Network").on("click", function(){

			if (me.palette=="AddNode") { // AddNodeモードの場合, クリックした位置にノードを追加する

				var tl = [me.transform.x, me.transform.y];
				var sc = me.transform.k;
				var MousePos = [(d3.mouse(this)[0] - tl[0])/sc, (d3.mouse(this)[1] - tl[1])/sc];
				// クリック位置のy座標を反転
				MousePos[1] = me.NodeYPos(MousePos[1]);

				// データにプッシュ
				// idは現配列に格納されているidの最大値+1
				var id = me.test_network.node.reduce((a,b)=>a.id>b.id?a:b).id + 1;
				var add_data = {"id":id, "pos":MousePos};
				me.test_network.node.push(add_data);

				// nodeを追加
				var g = d3.select("g.node");
				me.AddNode(g);
			}

		})
		.on("mousemove", function(){
			var tl = [me.transform.x, me.transform.y];
			var sc = me.transform.k;

			if (me.palette_sub==="SearchNode") {
				var pre_select = me.GetNodePos(me.test_network.node, me.now_target_node)
				d3.select("line.cursorLine")
					.attr("x1", (pre_select[0]*sc)+tl[0])
					.attr("y1", (me.YPos(pre_select[1])*sc+tl[1]))
					.attr("x2", d3.mouse(this)[0])
					.attr("y2", d3.mouse(this)[1]);
			} else if (me.palette==="AddNode") {

				d3.select("circle.cursorCircle")
					.attr("cx",d3.mouse(this)[0]).attr("cy",d3.mouse(this)[1]).attr("r",5);
			} else {
				true
			}
		})
		.on("mouseout", function(){
			d3.select("line.cursorLine")
				.attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 0);
			d3.select("circle.cursorCircle").attr("r",0);
		});
	},
	
  methods: {
		// zoom関数
		zoomed: function() {
			var me = this
			me.transform = d3.event.transform;
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
		YPos: function(v){ return this.height - v },

		// 画面の位置からYposを返す関数
		NodeYPos: function(v){ return this.height - v; },

		// 常に追加してあるエッジか否かを判定する関数
		CanAddEdge: function(v, h){

			var result = true

			if(v===h){
				result = false;
			}else{
				var me = this;
				var edge_list = [];
				me.test_network.edge.forEach(element => {
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

		ResetPaletteSub: function(){
			this.palette_sub = null;
			this.now_target_node = null;
		},

		// ノードを追加するメソッド(クリック時の挙動も定義するので関数化する)
		AddNode: function(g){
			var me = this;

			g.selectAll("circle").data(me.test_network.node, function(d){return d.id;}).enter().append("circle")
				.attr("cx", ({pos}) => pos[0]).attr("cy", ({pos}) => me.YPos(pos[1]))
				.attr("r", me.node_size)
				.on("click",function(d,idx,elem){

					if (me.palette==null){ // 編集モードが何も選択されていないとき
						var msg = "data:" + d.pos + " idx:" + idx + " elem:" + elem + " d3.event.pageX: " + d3.event.pageX + " d3.mouse: " + d3.mouse(this);
						alert(msg);
					} else if (me.palette=="AddEdge"){ // edgeを追加しているとき
						if (me.palette_sub=="SearchNode") { // tailノードを探しているとき
							if (me.CanAddEdge(me.now_target_node, d.id)) { // もしedgeをちゃんと追加できるなら

								var id = me.test_network.edge.reduce((a,b)=>a.id>b.id?a:b).id + 1
								var add_data = {"id":id, "head":me.now_target_node, "tail":d.id}
								me.test_network.edge.push(add_data)

								// エッジを追加
								me.AddEdge(d3.select("g.edge"))

								d3.select("line.cursorLine")
									.attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 0);

								me.palette_sub = null;
								me.now_target_node = null;
							}
						} else {
							me.now_target_node = d.id
							me.palette_sub = "SearchNode";
						}
						
					} else if (me.palette=="DeleteNode"){ // ノード削除モードのとき

						// ノードを削除
						me.DeleteNode(g, d.id);

						// 隣接したエッジを削除
						// 削除するエッジのidのリストを作成
						var delete_list = []
						me.test_network.edge.forEach(element => {
							if (element.head===d.id || element.tail===d.id ) {
								delete_list.push(element.id)
							}
						});
						delete_list = delete_list.filter(function (x, i, self) {
							return self.indexOf(x) === i;
						});
						var edge_g = d3.select("g.edge")
						delete_list.forEach(element => {
							me.DeleteEdge(edge_g, element)
						});

					}
				});
		},

		AddEdge: function(g){
			var me = this

			g.selectAll("line")
				.data(me.test_network.edge, function(d){return d.id}).enter()
				.append("line")
				.attr("x1", function(d){return me.GetNodePos(me.test_network.node, d.head)[0]})
				.attr("y1", function(d){return me.YPos(me.GetNodePos(me.test_network.node, d.head)[1])})
				.attr("x2", function(d){return me.GetNodePos(me.test_network.node, d.tail)[0]})
				.attr("y2", function(d){return me.YPos(me.GetNodePos(me.test_network.node, d.tail)[1])})
				.attr("stroke-width", 2)
				.attr("stroke", "black")
				.on("click",function(d,idx,elem){
					if (me.palette===null) {
						var msg = "data:" + d + " idx:" + idx + " elem:" + elem + " d3.event.pageX: " + d3.event.pageX + " d3.mouse: " + d3.mouse(this) ;
						alert(msg);
					} else if (me.palette==="DeleteEdge"){
						me.DeleteEdge(g, d.id)
					}
				});

		},

		// ノードを削除するメソッド
		DeleteNode: function(g, node_id){// node_idは削除するノードのid
			var me = this;
			// nodeリストから削除
			me.test_network.node = me.test_network.node.filter( function(item){ return item.id!==node_id; } );
			// 消されたリストを反映
			// data部分はidで設定しないと上手く消せない
			g.selectAll("circle").data(me.test_network.node, function(d){return d.id;}).exit().remove();
		},

		// エッジを削除するメソッド
		DeleteEdge: function(g, edge_id){
			var me = this;
			// edgeリストから削除
			me.test_network.edge = me.test_network.edge.filter( function(item){ return item.id!==edge_id; } );
			// 消されたリストを反映
			g.selectAll("line").data(me.test_network.edge, function(d){ return d.id; }).exit().remove();
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
		}
	}
}
</script>

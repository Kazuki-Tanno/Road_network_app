<template>
<div>
  this is edit.vue<br>
	<v-btn @click="BiggerNode(1)">BiggerNode</v-btn>
	<v-btn @click="BiggerNode(-1)">SmollerNode</v-btn>
	<v-btn @click="ChangeSVG(10)">SVG拡大</v-btn>
	<v-btn @click="ChangeSVG(-10)">SVG縮小</v-btn>
	<br><br>
	<svg :width="width" :height="height" :viewBox="viewBox"
	:style="style" class="Network">
	</svg>

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
			// 入力データ
			// ノードサイズ
			node_size: 1,
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
  created () {},

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
		this.AddNode();
	},
	
  methods: {
		ChangeSVG: function(n){
				this.height += n
				this.width += n
			},

		BiggerNode: function(n){
			this.node_size += n
			if (this.node_size < 0) {
				this.node_size = 0
			}
			const node = d3.select("g.node")
			node.selectAll("circle").data(this.test_network.node).attr("r", this.node_size)
		},

		AddNode:function(){
			
			// svgを検索
			var svg = d3.select("svg.Network")

			// svgのグループを作成
			const node = svg.append("g").attr("class", "node")

			// nodeを描画
			node.selectAll("circle")
        .data(this.test_network.node)
        .enter()
        .append("circle")
        .attr("cx", ({pos}) => pos[0]+50)
        .attr("cy", ({pos}) => pos[1]+50)
        .attr("r", this.node_size)
				.attr("fill", "#000000");

			// テキストを表示
			const text = svg.append("g")

			// テキストを描画
			text.selectAll("text")
				.data(this.test_network.node)
				.enter()
				.append("text")
				.text( 
					function(d){ return d.id + ": [" + String(d.pos) + "]" }
				)
				.attr("x", ({pos}) => pos[0]+50)
				.attr("y", ({pos}) => pos[1]+50)
				.attr("font-family", "sans-serif")
				.attr("font-size", "10px")
				.attr("text-anchor", "middle")
				.attr("dominant-baseline", "central")
				.attr("fill", "white");
		}
	}
}
</script>

<template>
<div>
  this is edit.vue
</div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'EditPage',

  // データプロパティ
  data () {
    return {
			// 入力データ
			// D3用のテストデータ
      test_network: {
        node: [
					{id:0, pos:[0,0], latlon:[4,5]},
					{id:1, pos:[2,0], latlon:[3,5]},
					{id:2, pos:[0,2], latlon:[4,2]},
					{id:3, pos:[2,2], latlon:[1,3]},
					{id:4, pos:[1,0.5], latlon:[4,5]}
        ],
				edge: [[0,1],[0,2],[1,3],[2,3],[0,4],[1,4]]
      } 
      
    }
  },

  // ライフサイクルフック関数
  created () {},

  // 算術プロパティ
  computed: {},

  // 監視プロパティ
  watch: {},

  mounted () { },

  methods: {}
}
</script>

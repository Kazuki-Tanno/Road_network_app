<template>
<div>
  this is home.vue<br>
  <v-file-input
  accept=".json, .geojson"
  label="File input"
  small-chips
  @change="getFileContent"
  ></v-file-input>
  {{ contents }}
  <br>
  <v-btn @click="SendData">データ送信</v-btn>
  <br>
  {{ result }}
</div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'HomePage',

  // データプロパティ
  data () {
    return {
      // 入力データ
      files: [],
      contents: '',
      result: ''
    }
  },

  // ライフサイクルフック関数
  created () {},

  // 算術プロパティ
  computed: {},

  // 監視プロパティ
  watch: {},

  mounted () { },

  methods: {
    
    // 入力ファイルの読み込み
    async getFileContent (file) {
      try {
        const content = await this.readFileAsync(file)
        this.contents = JSON.parse(content)
      } catch (e) {
        console.log(e)
      }
    },
    readFileAsync (file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => {
          resolve(reader.result)
        }
        reader.onerror = reject
        reader.readAsText(file)
      })
    },

    // バックエンドへの送信
    SendData: function(){

        // データが入力されていないとき
        if (this.contents==='') {
            alert('入力ファイルを指定してください')
        }
        //データが入力されている
        else{
            axios
            .post('/api/post', this.contents)
            .then(response => {
            this.result = response.data
            })
            .catch(err => {
                alert('APIサーバと接続できません')
                console.log(err)
            })
        }
    }
  }
}
</script>

<template>
  <div>
    <v-app-bar
      app
      elevation=1
      dense
    >
      <v-btn
        @click="root"
        text
      > Road Network Maker
      </v-btn>
    <v-spacer></v-spacer>
      <v-btn
        text
        @click="dialog = true"
      > How to use
      </v-btn>
    </v-app-bar>

    <!-- how to use欄 -->
    <v-dialog
      v-model="dialog"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition"
      scrollable
    >
      <v-card tile>
        <v-toolbar
          flat
          dark
        >
          <v-btn
            icon
            @click="dialog = false"
            dark
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>How to use</v-toolbar-title>
            <v-spacer></v-spacer>
          </v-toolbar>
          <v-card-text>
            <v-list
              subheader
            >
              <v-subheader>地図からネットワークを作成</v-subheader>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>多角形の作成</v-list-item-title>
                  <v-list-item-subtitle>
                    マップ左側にあるパレットを選択して，右の地図上で任意の多角形を作成してください．<br>
                    作成する多角形は1つのみである必要があります．<br>
                    また，あまりに大きすぎる多角形を選択した場合，ネットワークの生成に失敗する場合があります．
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>道路網のタイプを指定</v-list-item-title>
                  <v-list-item-subtitle>
                    ネットワークとして生成する道路網のタイプを左下のボタンから選択してください．<br>
                    各ネットワークタイプは<a href="https://osmnx.readthedocs.io/en/stable/index.html">OSMnx</a>の"network_type"に準拠しています．
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>ネットワークの簡略化度を指定</v-list-item-title>
                  <v-list-item-subtitle>
                    生成するネットワークの簡略化度を下部のスライドバーで指定してください．<br>
                    ここで指定した値が大きいほど，元の道路網の形状を保持します．<br>
                    例えば簡略度を150とした場合，次数が2で接続しているエッジが成す最小角が150度以上のノードを削除したネットワークを生成します．
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>末端ノードを削除するかを指定</v-list-item-title>
                  <v-list-item-subtitle>
                    末端ノードを削除するかを右下のラジオボックスで指定してください．<br>
                    チェックボックスをオンにした場合，次数が1のノードをすべて削除したネットワークが生成されます．
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>ネットワークを生成</v-list-item-title>
                  <v-list-item-subtitle>
                    右の生成ボタンを押して，多角形からネットワークを生成してください．<br>
                    生成に成功すると，右側のエディター画面にネットワークが表示されます．
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
            <v-divider></v-divider>
            <v-list
              subheader
              max-height="300"
            >
              <v-subheader>生成されたネットワークの調整</v-subheader>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>エディター画面で編集</v-list-item-title>
                  <v-list-item-subtitle>
                    エディター画面でネットワークを自由に編集してください．<br>
                    ノードの追加・削除，エッジの追加・削除に対応しています．<br>
                    Node Size，Edge Widthのスライドバーで，編集しやすいノードの大きさとエッジの太さに調整してください．
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>データの出力</v-list-item-title>
                  <v-list-item-subtitle>
                    右下のCSVで保存ボタンを押して，ネットワークを出力してください．<br>
                    ノードの位置情報のcsvファイルとエッジ情報のcsvファイルが，zip化されてダウンロードされます．<br>
                    ノードの位置情報は，ネットワークの中心を原点としたデカルト座標系(単位はメートル)に変換されています．<br>
                    緯度経度情報では無いので注意してください．
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
            <v-divider></v-divider>
            <v-list
              subheader
            >
              <v-subheader>その他</v-subheader>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>著作権について</v-list-item-title>
                  <v-list-item-subtitle>
                    当サイトはOpenStreetMapのデータを利用しています．<br>
                    また，当サイトで作成したデータは<a href="https://opendatacommons.org/licenses/odbl/1.0/">Open Data Licese</a>の下で利用できます．
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>不具合・バグについて</v-list-item-title>
                  <v-list-item-subtitle>
                    不具合・バグ等が見つかりましたら，nanyouhagi0605@gmail.com までご連絡いただければ幸いです．<br>
                    その他，ご意見・ご質問等がございましたら，上記のメールアドレスにお送りください．
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card-text>

          <div style="flex: 1 1 auto;"></div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  name:'header',

  data(){
    return {
      dialog: false
    }
  },

  methods: {
    root: function () {
      this.$router.push('/')
    }
  }

}
</script>

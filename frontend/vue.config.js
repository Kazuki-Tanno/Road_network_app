module.exports = {
  "assetsDir": "static",
  "transpileDependencies": [
    "vuetify"
  ],
  "devServer": {
    "port": "8080",
    "host": '127.0.0.1'
  },
  chainWebpack: config => {
    config.externals({
      leaflet: 'L'
    }),
    config.performance
      .maxEntrypointSize(400000)
      .maxAssetSize(400000)
  },
}
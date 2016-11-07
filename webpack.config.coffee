SOURCE = __dirname + "/src"
DEST   = __dirname + "/dist/assets"

module.exports =
  context: SOURCE
  entry:
    app: ["./client/app.coffee"]
  output:
    path: DEST
    filename: "bundle.js"
  resolve:
    extensions: ["", ".js", ".json", ".coffee"]
  # This is Webpack's cryptic way to get sourcemaps running
  # devtool: "#cheap-module-eval-source-map",
  devtool: "#inline-source-map",
  module:
    preLoaders: [{
      test: /\.coffee$/
      exclude: /node_modules/
      loader: "coffeelint-loader"
    }]
    loaders: [
      {test: /\.coffee$/, 		loaders: ["ng-annotate-loader", "coffee-loader"]}
      {test: /\.png$/,				loaders: ["file?name=[name].[ext]"]}
      {test: /\.scss$/, 			loaders: ["style", "css?sourceMap", "sass?sourceMap"]}
      {test: /\.slim$/, 			loaders: ["ngtemplate", "html", "slm"], exclude: /index\.slim$/}
      {test: /index\.slim$/,	loaders: ["file?name=[name].html", "extract", "html", "slm"]}
    ]

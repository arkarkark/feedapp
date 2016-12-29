SOURCE = __dirname + "/src"
DEST   = __dirname + "/dist/assets"

module.exports =
  context: SOURCE
  entry:
    vendor: [
      "angular"
      "angular-animate"
      "angular-aria"
      "angular-material"
      "angular-material/angular-material.css"
      "angular-messages"
      "angular-resource"
      "angular-route"
      "angular-sanitize"
      "font-awesome-webpack-sass"
      "./client/vendor.coffee"
    ]
  output:
    path: DEST
    filename: "bundle.vendor.js"
  devtool: "#cheap-module-eval-source-map",
  module:
    loaders: [
      {test: /\.coffee$/, 		loaders: ["ng-annotate-loader", "coffee-loader"]}
      {test: /\.css$/, 			  loaders: ["style", "css?sourceMap"]}
      {test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/, loader: "url-loader?limit=10000&minetype=application/font-woff&publicPath=assets/" }
      {test: /\.(ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/, loader: "file-loader?publicPath=assets/" }
    ]

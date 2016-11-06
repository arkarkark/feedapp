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
  devtool: "#cheap-module-eval-source-map",
  module:
    preLoaders: [{
      test: /\.coffee$/
      exclude: /node_modules/
      loader: "coffeelint-loader"
    }, {
      test: /\.coffee$/
      exclude: /node_modules/
      loader: "baggage?[file].html&[file.css]"
    }]
    loaders: [
      {test: /\.css$/, 				loader: "style!css"}
      {test: /\.coffee$/, 		loader: "ng-annotate-loader!coffee-loader"}
      {test: /index\.slim$/,	loader: "html!slm"}
      {test: /default\.slim$/, 			loader: "ngtemplate!html!slm"}
    ]

SOURCE = __dirname + "/src"
DEST   = __dirname + "/dist/assets"

module.exports =
  entry:
    vendor: [
      "angular"
      "angular-resource"
      "angular-route"
      "angular-sanitize"
      "bootstrap-loader"
    ]
  output:
    path: DEST
    filename: "bundle.vendor.js"
  devtool: "#cheap-module-eval-source-map",
  module:
    loaders: [
      {test:/bootstrap-sass[\/\\]assets[\/\\]javascripts[\/\\]/, loader: "imports?jQuery=jquery"}
      {test: /\.woff$/,   		loaders: ["url-loader?limit=10000&minetype=application/font-woff"]}
      {test: /\.woff2$/,      loaders: ["url?limit=10000"]}
      {test: /\.ttf$/,    		loaders: ["file-loader"]}
      {test: /\.eot$/,    		loaders: ["file-loader"]}
      {test: /\.svg$/,    		loaders: ["file-loader"]}
    ]

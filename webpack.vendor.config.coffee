SOURCE = __dirname + "/src"
DEST   = __dirname + "/dist/assets"

module.exports =
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
    ]
  output:
    path: DEST
    filename: "bundle.vendor.js"
  devtool: "#cheap-module-eval-source-map",
  module:
    loaders: [
      {test: /\.css$/, 			  loaders: ["style", "css?sourceMap"]}
        # {test: /\.woff$/,   		loaders: ["url-loader?limit=10000&minetype=application/font-woff"]}
        # {test: /\.woff2$/,      loaders: ["url?limit=10000"]}
        # {test: /\.ttf$/,    		loaders: ["file-loader"]}
        # {test: /\.eot$/,    		loaders: ["file-loader"]}
        # {test: /\.svg$/,    		loaders: ["file-loader"]}
    ]

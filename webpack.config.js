const path = require('path')
const webpack = require('webpack')
const CopyPlugin = require('copy-webpack-plugin')
const WriteFilePlugin = require('write-file-webpack-plugin')

module.exports = {
  mode: 'development',
  entry: './src/client/feedapp.coffee',
  //entry: './src/client/small.js',

  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist', 'assets')
  },

  plugins: [
    new webpack.ProgressPlugin(),
    new CopyPlugin([
      { from: '{app.yaml,index.yaml,requirements.txt,client_secrets.json,api_keys.json}', to: '../' },
      {
        from: './src/server/**/*',
        to: '../',
        ignore: ['*_test.py', 'flycheck_*'],
        transformPath (targetPath, absolutePath) {
          return '../' + targetPath.split('/').slice(3).join('/')
        }
      },
      {
        from: './testdata/*',
        to: '../',
      }
    ]),
    new WriteFilePlugin()
  ],

  module: {
    rules: [
      {
        test: /\.coffee$/,
        use: ["ng-annotate-loader", "coffee-loader"]
      },
      {
        test: /\.png$/,
        use: [
          {
            loader: "file-loader",
            options: {
                name: '[name].[ext]'
            }
          }
        ]
      },
      {
        test: /\.scss$/,
 	use: ["style-loader", "css-loader", "sass-loader"]
      },
      {
        test: /\.css$/,
 	use: ["style-loader", "css-loader"]
      },
      {
        test: /\.slim$/,
        use: ["ngtemplate-loader", "html-loader", "slm-loader"],
        exclude: new RegExp('index\.slim$')
      },
      {
        test: /index\.slim$/,
        use: [
          {
            loader: "file-loader",
            options: {
              name: "[name].html"
            }
          },
          "slm-loader"
        ]
      },
  {
        test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        use: [
          {
            loader: 'url-loader',
            options: {
              limit: 10000,
              mimetype: 'application/font-woff'
            }
          }
        ]
      },
      {
        test: /\.(ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        use: [
          { loader: 'file-loader' }
        ]
      }
    ]
  },

  devServer: {
    open: false,
    liveReload: false
  },

  resolve: {
    extensions: ['.tsx', '.ts', '.js', '.coffee']
  }
}

coffee  = require "gulp-coffee"
debug   = require "gulp-debug"
gulp    = require "gulp"
ignore  = require "gulp-ignore"
slm     = require "gulp-slm"
watch   = require "gulp-watch"
webpack = require "webpack-stream"

source =
  include: [
    "*.yaml"
    "testdata*/**/*"
    "src/server/**/*"
  ]
  webpack: [
    "src/client/**/*"
  ]

dirs =
  assets:      "dist/assets"
  destination: "dist"

handleError = ->
  (err) ->
    console.error(err.toString())
    @emit?("end")

gulp.task "default", ["webpack:build"], ->
  gulp.src(source.include).pipe(gulp.dest(dirs.destination))

gulp.task "webpack:build", ->
  gulp
    .src("src/client/app.coffee")
    .pipe(webpack(require("./webpack.config.coffee")))
    .pipe(gulp.dest(dirs.assets))

gulp.task "watch", ->
  watch(source.include).pipe(gulp.dest(dirs.destination))
  gulp.watch(source.webpack, ["webpack:build"])

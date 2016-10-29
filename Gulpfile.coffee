debug  = require "gulp-debug"
gulp   = require "gulp"
ignore = require "gulp-ignore"
slm    = require "gulp-slm"
watch  = require "gulp-watch"
coffee = require "gulp-coffee"

assets =
  include: [
    "*.yaml"
    "src/server/**/*"
    "src/client/**/*"
  ]
  exclude: [
    "**/*.coffee"
    "**/*.css"
    "**/*.slim"
  ]
  vendor: [
    "node_modules/angular-resource/angular-resource.min.js"
    "node_modules/angular-route/angular-route.min.js"
    "node_modules/angular/angular.min.js"
  ]

dirs =
  destination: "dist"
  assets:      "dist/assets"
  vendor:      "dist/assets/vendor"

handleError = ->
  (err) ->
    console.error(err.toString())
    @emit?("end")

gulp.task "default", ["slm", "coffee", "css", "vendor"], ->
  gulp.src(assets.include).pipe(ignore.exclude(assets.exclude)).pipe(gulp.dest(dirs.destination))

gulp.task "slm", ->
  gulp.src("src/client/**/*.slim")
    .pipe(debug())
    .pipe(slm({}).on("error", handleError("templates")))
    .pipe(gulp.dest(dirs.assets))

gulp.task "coffee", ->
  gulp.src("src/client/**/*.coffee")
    .pipe(debug())
    .pipe(coffee())
    .pipe(gulp.dest(dirs.assets))

gulp.task "css", ->
  gulp.src("src/client/**/*.css")
    .pipe(debug())
    .pipe(gulp.dest(dirs.assets))

gulp.task "vendor", ->
  gulp.src(assets.vendor)
    .pipe(debug())
    .pipe(gulp.dest(dirs.vendor))

gulp.task "watch", ->
  watch(assets.include)
    .pipe(ignore.exclude(assets.exclude))
    .pipe(gulp.dest(dirs.destination))
  watch("src/client/**/*.slim")
    .pipe(debug())
    .pipe(slm({}).on("error", handleError("templates")))
    .pipe(gulp.dest(dirs.assets))
  watch("src/client/**/*.coffee")
    .pipe(debug())
    .pipe(coffee())
    .pipe(gulp.dest(dirs.assets))
  watch("src/client/**/*.css")
    .pipe(debug())
    .pipe(gulp.dest(dirs.assets))

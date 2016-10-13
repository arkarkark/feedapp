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
    "**/*.slim"
    "**/*.coffee"
  ]

destination = "dist/"

gulp.task "default", ["slm", "coffee"], ->
  gulp.src(assets.include).pipe(ignore.exclude(assets.exclude)).pipe(gulp.dest(destination))

gulp.task "slm", ->
  gulp.src("src/client/**/*.slim")
    .pipe(slm({}))
    .pipe(gulp.dest(destination))

gulp.task "coffee", ->
  gulp.src("src/client/**/*.coffee")
    .pipe(coffee())
    .pipe(gulp.dest(destination))

gulp.task "watch", ->
  watch(assets.include).pipe(ignore.exclude(assets.exclude)).pipe(gulp.dest(destination))
  watch("src/client/**/*.slim").pipe(slm({})).pipe(gulp.dest(destination))
  watch("src/client/**/*.coffee").pipe(coffee()).pipe(gulp.dest(destination))

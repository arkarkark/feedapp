gulp = require "gulp"
watch = require "gulp-watch"

assets = [
  "*.yaml"
  "src/server/**/*"
  "src/client/**/*"
]

destination = "app/"

gulp.task "default", ->
  gulp.src(assets).pipe(gulp.dest(destination))

gulp.task "watch", ->
  watch(assets).pipe(gulp.dest(destination))

m = require "./blogger_module"

require "./blogger_resource"

module.exports = ($scope, Blogger) ->
  $scope.loading = true
  $scope.blogs = Blogger.query -> $scope.loading = false

  $scope.addByUrl = (url, name) ->
    console.log("Adding by url", url)
    blog = new Blogger(blog_url: url, name: name)
    blog.$save (blog) ->
      $scope.byUrl = ""
      $scope.name = ""
      existing = _.findWhere($scope.blogs, blog_id: blog.blog_id)
      if existing
        console.log("Updating existing\n", JSON.stringify(existing), "\n", JSON.stringify(blog))
        _.extend(existing, blog)
      else
        $scope.blogs.push(blog)

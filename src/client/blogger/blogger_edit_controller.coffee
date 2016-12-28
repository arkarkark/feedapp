require "./blogger_resource"

module.exports = ($scope, $routeParams, Blogger) ->
  $scope.loading = true
  console.log("blog_id", $routeParams.blog_id)
  $scope.blog = Blogger.get({blog_id: $routeParams.blog_id}, -> $scope.loading = false)

  $scope.update = (blog) ->
    blog = new Blogger(blog)
    promise = blog.$save (blog) ->
      $scope.blog = blog

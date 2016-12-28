module.exports = (
  $location
  $routeParams
  $scope
  Blogger
) ->
  $scope.loading = true
  $scope.blog = Blogger.get({blog_id: $routeParams.blog_id}, -> $scope.loading = false)

  $scope.update = (blog) ->
    blog = new Blogger(blog)
    blog.$save (blog) ->
      $scope.blog = blog

  $scope.delete = (blog) ->
    Blogger.delete {blog_id: blog.blog_id}, ->
      $location.path("/blogger")

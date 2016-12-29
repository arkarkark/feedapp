module.exports = (
  $location
  $routeParams
  $scope
  Blogger
) ->
  $scope.loading = true
  $scope.blog = Blogger.get({blog_id: $routeParams.blog_id}, -> $scope.loading = false)

  $scope.delete = (blog) ->
    Blogger.delete {blog_id: blog.blog_id}, ->
      $scope.done()

  $scope.done = ->
    $location.path("/blogger")

  $scope.update = (blog) ->
    blog = new Blogger(blog)
    blog.$save (blog) ->
      $scope.blog = blog

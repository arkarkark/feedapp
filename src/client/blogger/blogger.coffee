m = angular.module('bloggerServices', [ 'ngResource' ])


m.factory 'Blogger', ($resource) ->
  $resource 'data/blogger/feed.json?blog_id=:blog_id', { blog_id: '@blog_id' }, {}

m.controller "BloggerCtrl", ($scope, $routeParams, $location, Blogger) ->
  blog_id = 'new'
  if $routeParams.blog_id
    blog_id = $routeParams.blog_id
  $scope.blogs = Blogger.query (ans) ->
    i = 0
    while i < $scope.blogs.length
      blog = $scope.blogs[i]
      if blog.blog_id == blog_id
        $scope.blog = blog
        break
      i++
    return

  $scope.update = ->
    $scope.blog.$save (ans) ->
      console.log 'name, keep_first: ' + $scope.blog.name + ' / ' + $scope.blog.keep_first
      $scope.blogs = Blogger.query()
      $location.path '/blogger'
      return
    return

  return

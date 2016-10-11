'use strict';

angular.module('bloggerServices', ['ngResource']).
  factory('Blogger', function($resource) {
    return $resource('data/blogger/feed.json?blog_id=:blog_id',
                     {blog_id: '@blog_id'}, {});
  });

function BloggerCtrl($scope, $routeParams, $location, Blogger) {
  var blog_id = 'new';
  if ($routeParams.blog_id) {
    blog_id = $routeParams.blog_id;
  }
  $scope.blogs = Blogger.query(function(ans) {
    for (var i = 0; i < $scope.blogs.length; i++) {
      var blog = $scope.blogs[i];
      if (blog.blog_id == blog_id) {
        $scope.blog = blog;
        break;
      }
    }
  });

  $scope.update = function() {
    $scope.blog.$save(function(ans) {
      console.log('name, keep_first: ' + $scope.blog.name + ' / ' +
                  $scope.blog.keep_first);
      $scope.blogs = Blogger.query();
      $location.path('/blogger');
    });
  };
}

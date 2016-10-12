'use strict';

angular.module('userServices', ['ngResource']).
  factory('User', function($resource) {
    return $resource('data/user/user.json', {}, {});
  });


function HeaderCtrl($scope, User) {
  $scope.$parent.user = User.get();
}

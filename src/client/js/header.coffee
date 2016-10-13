HeaderCtrl = ($scope, User) ->
  $scope.$parent.user = User.get()
  return

'use strict'
angular.module('userServices', [ 'ngResource' ]).factory 'User', ($resource) ->
  $resource 'data/user/user.json', {}, {}

"use strict"
m = angular.module("userServices", [ "ngResource" ])

m.factory "User", ($resource) ->
  $resource "data/user/user.json", {}, {}

m.controller "HeaderCtrl", ($scope, User) ->
  $scope.$parent.user = User.get()
  return this

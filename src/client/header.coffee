m = require "./header_module.coffee"

m.factory "User", ($resource) ->
  $resource "data/user/user.json", {}, {}

m.controller "HeaderCtrl", ($scope, User) ->
  $scope.$parent.user = User.get()
  return this

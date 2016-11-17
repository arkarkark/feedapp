m = require("./blogger_module")

require "./blogger_resource"

module.exports = m.controller "BloggerListController", ($scope, Blogger) ->
  $scope.blogs = Blogger.query()

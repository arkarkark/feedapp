m = require "./blogger_module"

bloggerEditTemplate = require "./blogger_edit.slim"
bloggerEditController = require "./blogger_edit_controller"

m.config ($routeProvider) ->
  $routeProvider.when "/blogger/edit/:blog_id",
      templateUrl: bloggerEditTemplate
      controller: bloggerEditController

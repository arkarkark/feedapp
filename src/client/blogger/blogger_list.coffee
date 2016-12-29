m = require "./blogger_module"

require "./blogger_list.scss"

bloggerListTemplate = require "./blogger_list.slim"
bloggerListController = require "./blogger_list_controller"

m.config ($routeProvider) ->
  $routeProvider.when "/blogger",
      templateUrl: bloggerListTemplate
      controller: bloggerListController

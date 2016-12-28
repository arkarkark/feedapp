module.exports = m = angular.module "bloggerServices", ["ngResource"]

bloggerListTemplate = require "./blogger_list.slim"
bloggerListController = require "./blogger_list_controller"

bloggerEditTemplate = require "./blogger_edit.slim"
bloggerEditController = require "./blogger_edit_controller"

m.config ($routeProvider) ->
  $routeProvider
    .when("/blogger",
      templateUrl: bloggerListTemplate
      controller: bloggerListController
    ).when("/blogger/edit/:blog_id",
      templateUrl: bloggerEditTemplate
      controller: bloggerEditController
    )

module.exports = m = angular.module "bloggerServices", ["ngResource"]

bloggerListTemplate = require "./blogger_list.slim"
bloggerListController = require "./blogger_list_controller"

bloggerEditTemplate = require "./blogger_edit.slim"

m.config ($routeProvider) ->
  $routeProvider
    .when("/blogger",
      templateUrl: bloggerListTemplate
      controller: bloggerListController
    ).when("/blogger/edit/:id",
      templateUrl: bloggerEditTemplate
      # controller: "MailEditController"
    )

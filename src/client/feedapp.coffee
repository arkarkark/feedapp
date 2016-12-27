require "./index.slim"
require "./index.scss"
require "./rss.png"
defaultTemplate = require "./default.slim"

m = angular.module "feedapp", [
  "ngMaterial"
  "ngRoute"
  "ngSanitize"
  require("./header_module").name
  require("./mail/mail_module").name
  require("./blogger/blogger_module").name
  # "expandServices"
  # "bloggerServices"
]

m.config ($routeProvider) ->
  $routeProvider
    .when(
      "/"
      templateUrl: defaultTemplate
    ).when("/expand",
      templateUrl: "assets/static/expand-list.html"
      controller: "ExpandCtrl"
    ).when("/expand/edit/:id",
      templateUrl: "assets/static/expand-edit.html"
      controller: "ExpandCtrl"
    ).otherwise "/"
  return

m.config ($locationProvider) ->
  # Use html5paths - all url navigation will be done within angular,
  $locationProvider.html5Mode(enabled: true, requireBase: false)

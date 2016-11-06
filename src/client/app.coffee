require "./index.slim"

angular = require "angular"

require "angular-route"

console.log("SLIM", require "./default.slim")

m = angular.module "feedapp", [
  "ngRoute"
  require("./header_module").name
  require("./mail/mail_module").name
  # "expandServices"
  # "bloggerServices"
]

m.config ($routeProvider) ->
  $routeProvider
    .when(
      "/"
      templateUrl: require "./default.slim"
    ).when(
      "/blogger"
      templateUrl: "assets/static/blogger-list.html"
      controller: "BloggerCtrl"
    ).when(
      "/blogger/edit/:blog_id",
      templateUrl: "assets/static/blogger-edit.html"
      controller: "BloggerCtrl"
    ).when("/expand",
      templateUrl: "assets/static/expand-list.html"
      controller: "ExpandCtrl"
    ).when("/expand/edit/:id",
      templateUrl: "assets/static/expand-edit.html"
      controller: "ExpandCtrl"
    ).when("/mail",
      templateUrl: "/assets/mail/mail.html"
      controller: "MailCtrl"
    ).when("/mail/edit/:id",
      templateUrl: "/assets/mail/mail_edit.html"
      controller: "MailEditController"
    ).otherwise "/"
  return

m.config ($locationProvider) ->
  # Use html5paths - all url navigation will be done within angular,
  $locationProvider.html5Mode(enabled: true, requireBase: false)

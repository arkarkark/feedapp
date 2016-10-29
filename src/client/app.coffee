"use strict"

m = angular.module "feedapp", [
  "ngRoute"
  "userServices"
  "expandServices"
  "bloggerServices"
  "mailServices"
]

m.controller "DefaultCtrl", ->

m.config ($routeProvider) ->
  $routeProvider
    .when(
      "/"
      templateUrl: "assets/default.html"
      controller: "DefaultCtrl"
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
      templateUrl: "assets/mail/mail-list.html"
      controller: "MailCtrl"
    ).when("/mail/edit/:id",
      templateUrl: "assets/mail/mail-edit.html"
      controller: "MailCtrl"
    ).otherwise "/"
  return

m.config ($locationProvider) ->
  # Use html5paths - all url navigation will be done within angular,
  $locationProvider.html5Mode(enabled: true, requireBase: false)

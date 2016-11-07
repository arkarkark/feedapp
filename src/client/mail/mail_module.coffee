angular = require "angular"

module.exports = m = angular.module "mailServices", [ "ngResource" ]

mailTemplate = require "./mail.slim"
mailEditTemplate = require "./mail_edit.slim"

require "./mail_resource"
require "./mail"
require "./mail_edit_controller"

m.config ($routeProvider) ->
  $routeProvider
    .when("/mail",
      templateUrl: mailTemplate
      controller: "MailCtrl"
    ).when("/mail/edit/:id",
      templateUrl: mailEditTemplate
      controller: "MailEditController"
    )

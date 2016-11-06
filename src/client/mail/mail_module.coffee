angular = require "angular"

module.exports = angular.module "mailServices", [ "ngResource" ]

require "./mail_resource"
require "./mail"
require "./mail_edit_controller"

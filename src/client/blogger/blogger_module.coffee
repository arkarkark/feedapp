module.exports = m = angular.module "bloggerServices", ["ngResource"]

m.service "Blogger", require "./blogger_resource"

require "./blogger_list"
require "./blogger_edit"

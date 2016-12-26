m = require("./blogger_module")

m.service "Blogger", ($resource) -> $resource "data/blogger/blog"

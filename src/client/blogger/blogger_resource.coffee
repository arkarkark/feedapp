m = require("./blogger_module")

m.factory "Blogger", ($resource) ->
  $resource "/data/blogger/feed.json?blog_id=:blog_id", { blog_id: "@blog_id" }, {}

module.exports = ($scope, Blogger) ->
  $scope.sort = "title"
  $scope.loading = true
  $scope.blogs = Blogger.query -> $scope.loading = false

  $scope.addByUrl = (url, name) ->
    console.log("Adding by url", url)
    $scope.create(url: url, name: name).then ->
      $scope.byUrl = ""
      $scope.name = ""

  $scope.create = (blog) ->
    blog = new Blogger(blog)
    promise = blog.$save (blog) ->
      console.log("looking for ", blog.blog_id)
      existing = _.findWhere($scope.blogs, blog_id: blog.blog_id)
      if existing
        console.log("Updating existing\n", JSON.stringify(existing), "\n", JSON.stringify(blog))
        _.extend(existing, blog)
      else
        $scope.blogs.push(blog)

    return promise

  $scope.setSort = (thing) ->
    b = $scope.sort
    if $scope.sort == thing
      $scope.sort = "-#{thing}"
    else
      $scope.sort = thing
    console.log("setSort", b, thing, $scope.sort)

  $scope.sortOrder = (name) ->
    switch $scope.sort
      when name then "^"
      when "-#{name}" then "v"
      else ""

m = require "./mail_module"

m.controller "MailEditController", (
  $location
  $routeParams
  $scope
  $timeout
  MailFeed
  MailFeedItem
) ->
  id = "new"
  if $routeParams.id
    id = $routeParams.id
  $scope.feed = MailFeed.get(id: id)
  $scope.items = MailFeedItem.query({ parent_id: id }, ->
    $scope.selectItem $scope.items[0].id if $scope.items.length
    return
  )
  $scope.stripScripts = (a) -> a # TODO(ark): use $sce sanitize thing

  goToMail = ->
    $timeout(
      -> $location.path "/mail"
      200
    )

  $scope.update = ->
    $scope.feed.$save (ans) ->
      goToMail()

  $scope.remove = ->
    if confirm("""Are you sure you want to remove feed "#{$scope.feed.name}" ?""")
      $scope.feed.$remove (ans) ->
        goToMail()
    return

  $scope.cancel = ->
    $location.path "/mail"
    return

  $scope.selectItem = (itemId) ->
    $scope.item = MailFeedItem.get(
      id: itemId
      parent_id: id
    )

  $scope.tombstoneItem = ->
    $scope.item.$tombstone()
    # update the item in items
    i = 0
    while i < $scope.items.length
      if $scope.items[i].id == $scope.item.id
        $scope.items[i] = $scope.item
        break
      i++
    return

  return this

m = require "./mail_module"

m.factory "MailFeed", ($resource) ->
  $resource "/data/mail/feed.json?id=:id", { id: "@id" }, {}

m.factory "MailFeedItem", ($resource) ->
  $resource(
    "/data/mail/item.json?id=:id&parent_id=:parent_id&action=:action"
    {
      id: "@id"
      parent_id: "@parent_id"
    }
    {
      tombstone:
        method: "POST"
        params: action: "tombstone"
    }
  )

m.controller "MailCtrl", (
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
  $scope.feeds = MailFeed.query()
  $scope.feed = MailFeed.get(id: id)
  $scope.items = MailFeedItem.query({ parent_id: id }, ->
    $scope.selectItem $scope.items[0].id if $scope.items.length
    return
  )

  $scope.update = ->
    console.log("Saving")
    $scope.feed.$save (ans) ->
      console.log("Saved")
      $timeout(
        -> $scope.feeds = MailFeed.query()
        2000
      )
      $location.path "/mail"
      return
    return

  $scope.remove = ->
    if confirm("""Are you sure you want to remove feed "#{$scope.feed.name}" ?""")
      $scope.feed.$remove (ans) ->
        $scope.feeds = MailFeed.query (feeds) ->
          console.log(JSON.stringify(feeds, null, 2))
        $location.path "/mail"
        return
    return

  $scope.cancel = ->
    $location.path "/mail"
    return

  $scope.selectItem = (itemId) ->
    $scope.item = MailFeedItem.get(
      id: itemId
      parent_id: id)
    return

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

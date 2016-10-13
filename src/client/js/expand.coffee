ExpandCtrl = ($scope, $routeParams, $location, Expand, ExpandItem) ->
  id = 'new'
  if $routeParams.id
    id = $routeParams.id
  $scope.expands = Expand.query()
  $scope.expand = Expand.get(id: id)
  $scope.items = ExpandItem.query(
    id: ''
    parent_id: id)
  $scope.feed_types = [
    {
      value: 0
      name: 'rss'
    }
    {
      value: 1
      name: 'html page'
    }
    {
      value: 2
      name: 'html link list'
    }
  ]

  $scope.update = ->
    $scope.expand.$save (ans) ->
      $scope.expands = Expand.query()
      $location.path '/expand'
      return
    return

  $scope.remove = ->
    if confirm('Are you sure you want to remove feed "' + $scope.expand.name + '" ?')
      $scope.expand.$remove (ans) ->
        # redirect to the main page
        $scope.expands = Expand.query()
        $location.path '/expand'
        return
    return

  $scope.cancel = ->
    $location.path '/expand'
    return

  $scope.clearAllItems = ->
    alert 'TODO(ark) clearing!'
    return

  $scope.selectItem = (itemId) ->
    $scope.item = ExpandItem.get({
      parent_id: id
      id: itemId
    }, ->
      $scope.item.cleanBody = stripScripts($scope.item.body)
      return
    )
    return

  $scope.refreshItem = ->
    $scope.item.expand = $scope.expand
    $scope.item.$preview { parent_id: id }, (item) ->
      item.cleanBody = stripScripts(item.body)
      return
    return

  $scope.importExport = ->
    ans = prompt('got json?', JSON.stringify($scope.expand))
    if ans
      n = JSON.parse(ans)
      for v of n
        if v == 'id'
          continue
        if $scope.expand.hasOwnProperty(v)
          $scope.expand[v] = n[v]
    return

  return

m = angular.module('expandServices', [ 'ngResource' ])

m.factory 'Expand', ($resource) ->
  $resource 'data/expand/feed.json?id=:id', { id: '@id' }, {}


m.factory 'ExpandItem', ($resource) ->
  $resource(
    'data/expand/item.json?' + 'id=:id&parent_id=:parent_id&action=:action'
    {
      id: '@id'
      parent_id: '@parent_id'
    }
    {
      preview:
        method: 'POST'
        params: action: 'preview'
    }
  )

'use strict';

angular.module('expandServices', ['ngResource']).
  factory('Expand', function($resource) {
    return $resource('data/expand/feed.json?id=:id', {id: '@id'}, {});
  }).
  factory('ExpandItem', function($resource) {
    return $resource('data/expand/item.json?' +
                     'id=:id&parent_id=:parent_id&action=:action',
                     {id: '@id', parent_id: '@parent_id'},
                     {preview: {method: 'POST', params: {action: 'preview'}}});
  });

function ExpandCtrl($scope, $routeParams, $location, Expand, ExpandItem) {
  var id = 'new';
  if ($routeParams.id) {
    id = $routeParams.id;
  }
  $scope.expands = Expand.query();
  $scope.expand = Expand.get({id: id});
  $scope.items = ExpandItem.query({id: '', parent_id: id});

  $scope.feed_types = [
    {value: 0, name: 'rss'},
    {value: 1, name: 'html page'},
    {value: 2, name: 'html link list'}
  ];

  $scope.update = function() {
    $scope.expand.$save(function(ans) {
      $scope.expands = Expand.query();
      $location.path('/expand');
    });
  };
  $scope.remove = function() {
    if (confirm('Are you sure you want to remove feed "' +
                $scope.expand.name + '" ?')) {
      $scope.expand.$remove(function(ans) {
        // redirect to the main page
        $scope.expands = Expand.query();
        $location.path('/expand');
      });
    }
  };

  $scope.cancel = function() {
    $location.path('/expand');
  };

  $scope.clearAllItems = function() {
    alert('TODO(ark) clearing!');
  };

  $scope.selectItem = function(itemId) {
    $scope.item = ExpandItem.get({parent_id: id, id: itemId},
                                 function() {
        $scope.item.cleanBody = stripScripts($scope.item.body);
      });
  };

  $scope.refreshItem = function() {
    $scope.item.expand = $scope.expand;
    $scope.item.$preview({parent_id: id}, function(item) {
      item.cleanBody = stripScripts(item.body);
    });
  };

  $scope.importExport = function() {
    var ans = prompt("got json?", JSON.stringify($scope.expand));
    if (ans) {
      var n = JSON.parse(ans);
      for (var v in n) {
        if (v == 'id') {
          continue;
        }
        if ($scope.expand.hasOwnProperty(v)) {
          $scope.expand[v] = n[v];
        }
      }
    }
  }
}

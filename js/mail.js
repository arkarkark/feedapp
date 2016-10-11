'use strict';

angular.module('mailServices', ['ngResource']).
  factory('MailFeed', function($resource) {
    return $resource('data/mail/feed.json?id=:id', {id: '@id'}, {});
  }).
  factory('MailFeedItem', function($resource) {
    return $resource('data/mail/item.json' +
                     '?id=:id&parent_id=:parent_id&action=:action',
                     {id: '@id', parent_id: '@parent_id'},
                     {tombstone: {method: 'POST',
                                  params: {action: 'tombstone'}}});
  });


function MailCtrl($scope, $routeParams, $location, MailFeed, MailFeedItem) {
  var id = 'new';
  if ($routeParams.id) {
    id = $routeParams.id;
  }
  $scope.feeds = MailFeed.query();
  $scope.feed = MailFeed.get({id: id});
  $scope.items = MailFeedItem.query({parent_id: id}, function() {
    $scope.selectItem($scope.items[0].id);
  });

  $scope.stripScripts = stripScripts;

  $scope.update = function() {
    $scope.feed.$save(function(ans) {
      $scope.feeds = MailFeed.query();
      $location.path('/mail');
    });
  };

  $scope.remove = function() {
    if (confirm('Are you sure you want to remove feed "' +
                $scope.feed.feed_name + '" ?')) {
      $scope.feed.$remove(function(ans) {
        $scope.feeds = MailFeed.query();
        $location.path('/mail');
      });
    }
  };

  $scope.cancel = function() {
    $location.path('/mail');
  };


  $scope.selectItem = function(itemId) {
    $scope.item = MailFeedItem.get({id: itemId, parent_id: id});
  };

  $scope.tombstoneItem = function() {
    $scope.item.$tombstone();
    // update the item in items
    for (var i = 0; i < $scope.items.length; i++) {
      if ($scope.items[i].id == $scope.item.id) {
        $scope.items[i] = $scope.item;
        break;
      }
    }
  };

}

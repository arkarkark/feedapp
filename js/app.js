'use strict';

function DefaultCtrl($scope) {}

angular.module('feedapp',
               ['userServices', 'expandServices',
                'bloggerServices', 'mailServices']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.
      when('/',
           {templateUrl: 'static/default.html',
            controller: DefaultCtrl}).
      when('/blogger',
           {templateUrl: 'static/blogger-list.html',
            controller: BloggerCtrl}).
      when('/blogger/edit/:blog_id',
           {templateUrl: 'static/blogger-edit.html',
            controller: BloggerCtrl}).
      when('/expand',
           {templateUrl: 'static/expand-list.html',
            controller: ExpandCtrl}).
      when('/expand/edit/:id',
           {templateUrl: 'static/expand-edit.html',
            controller: ExpandCtrl}).
      when('/mail',
           {templateUrl: 'static/mail-list.html',
            controller: MailCtrl}).
      when('/mail/edit/:id',
           {templateUrl: 'static/mail-edit.html',
            controller: MailCtrl}).
      otherwise({redirectTo: '/'});
  }]);

'use strict';

/**
 * @ngdoc overview
 * @name opendatahubApp
 * @description
 * # opendatahubApp
 *
 * Main module of the application.
 */
angular
    .module('opendatahubApp', [
        'ngAnimate',
        'ngAria',
        'ngCookies',
        'ngMessages',
        'ngResource',
        'ngRoute',
        'ngSanitize',
        'ngTouch'
    ])
    .config(function ($routeProvider) {
        $routeProvider
            .when('/', {
                templateUrl: 'views/main.html',
                controller: 'MainCtrl'
            })
            .when('/about', {
                templateUrl: 'views/about.html',
                controller: 'AboutCtrl'
            })
            .when('/PlumbDemo', {
              templateUrl: 'views/plumbdemo.html',
              controller: 'PlumbdemoCtrl'
            })
            .otherwise({
                redirectTo: '/'
            });
    });

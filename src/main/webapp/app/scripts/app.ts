/// <reference path='../../typings/tsd.d.ts' />
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
        'ngSanitize',
        'ngTouch',
        'ui.router',
        'ui.utils',
        'ui.select',
        'ngToast'
    ])
    .config(function ($stateProvider, $urlRouterProvider, ngToastProvider) {

        // Toast config
        ngToastProvider.configure({
            horizontalPosition: 'center'
        });

        $urlRouterProvider.otherwise('/');

        $stateProvider
            .state('main', {
                url: '/',
                templateUrl: 'views/main.html'
            })
            .state('offer', {
                controller: 'OfferCtrl',
                templateUrl: 'views/offer.html',
                controllerAs: 'vm'
            })
            .state('about', {
                controller: 'AboutCtrl',
                templateUrl: 'views/about.html'
            });
    });

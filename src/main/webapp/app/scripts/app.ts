/// <reference path='all.d.ts' />

module openDataHub {
    'use strict';
    var openDataHub = angular
        .module('openDataHub', [
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
            'ngToast',
            'openDataHub.routes',
            'openDataHub.auth',
        ]);

    var openDataAuth = angular
        .module('openDataHub.auth', []);

    var openDataRoutes = angular
        .module('openDataHub.routes', ['ui.router']);

    angular
        .module('openDataHub')
        .config(config)
        .run(run);

    function run($http) {
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
    }

    function config($stateProvider:ng.ui.IStateProvider, $locationProvider:ng.ILocationProvider, ngToastProvider) {

        // Toast config
        ngToastProvider.configure({
            horizontalPosition: 'center'
        });

        $stateProvider
            .state('main', {
                url: '/',
                templateUrl: 'views/main.html'
            })
            .state('offer', {
                url: '/offer',
                controller: 'OfferController as offer',
                templateUrl: 'views/offer.html'
            })
            .state('offer.params', {
                url: '/:type',
                controller: 'OfferParamsController as params',
                templateUrl: 'views/offer.params.html'
            })
            .state('register', {
                url: '/register',
                controller: 'RegisterController as vm',
                templateUrl: '/views/authentication/register.html'
            })
            .state('login', {
                url: '/login',
                controller: 'LoginController as vm',
                templateUrl: '/views/authentication/login.html'
            })
            .state('about', {
                controller: 'AboutCtrl',
                templateUrl: 'views/about.html'
            });
    }
}

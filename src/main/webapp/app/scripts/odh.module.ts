/// <reference path='all.d.ts' />


module openDataHub {
    'use strict';
    angular
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
            'openDataHub.auth',
            'openDataHub.utils'
        ]);

    angular
        .module('openDataHub')
        .config(config)
        .run(run);

    function run($http:ng.IHttpService) {
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
    }

    function config($stateProvider:ng.ui.IStateProvider, $locationProvider:ng.ILocationProvider, ngToastProvider) {

        ngToastProvider.configure({
            horizontalPosition: 'center',
            verticalPosition: 'top',
            animation: 'slide'
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
            .state('userDetail',
            {
                url: '/:username',
                controller: 'AccountController as vm',
                templateUrl: '/views/authentication/account.html'
            })
            .state('userSettings',
            {
                url: '/:username/settings',
                controller: 'AccountSettingsController as vm',
                templateUrl: '/views/authentication/settings.html'
            });
    }
}

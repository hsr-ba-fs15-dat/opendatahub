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
            'openDataHub.auth',
        ]);

    var openDataAuth = angular
        .module('openDataHub.auth', []);


    angular
        .module('openDataHub')
        .config(config)
        .run(run);

    function run($http) {
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
    }

    function config($stateProvider:ng.ui.IStateProvider) {
        $stateProvider
            .state('main', {
                url: '/',
                templateUrl: 'views/main.html'
            })
            //.state('offer', {
            //    controller: 'OfferCtrl',
            //    templateUrl: 'views/offer.html',
            //    controllerAs: 'vm'
            //})
            //.state('about', {
            //    controller: 'AboutCtrl',
            //    templateUrl: 'views/about.html'
            //})
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
                url: '/+:username',
                controller: 'AccountController as vm',
                templateUrl: '/views/authentication/account.html'
            })
            .state('userSettings',
            {
                url: '/+:username/settings',
                controller: 'AccountSettingsController as vm',
                templateUrl: '/views/authentication/settings.html'
            });

    }
}

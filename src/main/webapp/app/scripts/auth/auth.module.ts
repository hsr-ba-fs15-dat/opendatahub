/// <reference path='../all.d.ts' />

module odh.auth {
    'use strict';
    angular
        .module(
        'openDataHub.auth', [
            'ngCookies',
            'ngResource',
            'ngSanitize',
            'ngRoute',
            'ezfb',
            'restangular'
        ]
    ).config(config)
        ;

    function config($stateProvider:ng.ui.IStateProvider, ezfbProvider) {
        ezfbProvider.setLocale('de_DE');
        ezfbProvider.setInitParams({
            // appId: '401522313351953', // This is the Local ID
            appId: '401520096685508', // This is the Heroku ID
            version: 'v2.0'
        });
        $stateProvider

            .state('login', {
                url: '/login',
                controller: 'LoginController as lc',
                templateUrl: 'views/authentication/login.html',
                resolve: {
                    authenticated: ['AuthenticationService', function (AuthenticationService) {
                        return AuthenticationService.isAuthed();
                    }]
                }
            })
            .state('userProfile', {
                url: '/userProfile',
                controller: 'UserProfileController as up',
                templateUrl: '/views/authentication/userprofile.html'
                //
            })
            .state('logout', {
                url: '/logout',
                controller: 'LogoutController',
                templateUrl: '/views/authentication/logout.html',
                resolve: {
                    authenticated: ['AuthenticationService', function (AuthenticationService) {
                        return AuthenticationService.isAuthed();
                    }]
                }
            });

    }
}

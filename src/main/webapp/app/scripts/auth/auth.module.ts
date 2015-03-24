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
            'restangular',
            'satellizer'
        ]
    ).config(config)
    ;

    function config($stateProvider:ng.ui.IStateProvider, $authProvider) {
        $authProvider.facebook({
            url: '/api/v1/auth/social/',
            clientId: '401522313351953',
            responseType: 'token'
        });
        $authProvider.github({
            url: '/api/v1/auth/social/',
            clientId: 'f29d882c342818c82e0b'
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

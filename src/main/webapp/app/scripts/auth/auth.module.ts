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
        ]
    ).config(config)
        .run(function (AuthenticationService) {
            AuthenticationService.initialize('//192.168.56.101:5000/rest-auth', false);

        });
    ;
    function config($stateProvider:ng.ui.IStateProvider, $locationProvider:ng.ILocationProvider) {


        $stateProvider
            .state('demo', {
                url: '/demo',
                controller: 'MainController as mc',

                templateUrl: 'views/authentication/main.html',
                resolve: {
                    authenticated: ['AuthenticationService', function (AuthenticationService) {
                        return AuthenticationService.authenticationStatus();
                    }]
                }
            })
            .state('register', {
                url: '/register',
                controller: 'RegisterController as rc',

                templateUrl: 'views/authentication/register.html',
                resolve: {
                    authenticated: ['AuthenticationService', function (AuthenticationService) {
                        return AuthenticationService.authenticationStatus();
                    }]
                }
            })
            .state('passwordReset', {
                url: '/passwordReset',
                controller: 'PasswordResetController',
                templateUrl: 'views/authentication/passwordreset.html',
                resolve: {
                    authenticated: ['AuthenticationService', function (AuthenticationService) {
                        return AuthenticationService.authenticationStatus();
                    }]
                }
            })
            .state('login', {
                url: '/login',
                controller: 'LoginController',
                templateUrl: 'views/authentication/login.html',
                resolve: {
                    authenticated: ['AuthenticationService', function (AuthenticationService) {
                        return AuthenticationService.authenticationStatus();
                    }]
                }
            })
            .state('logout', {
                url: '/logout',
                controller: 'LogoutController',
                templateUrl: '/views/authentication/logout.html',
                resolve: {
                    authenticated: ['AuthenticationService', function (AuthenticationService) {
                        return AuthenticationService.authenticationStatus();
                    }]
                }
            })
            .state('userProfile', {
                url: '/userProfile',
                controller: 'UserProfileController',
                templateUrl: '/views/authentication/userprofile.html',
                resolve: {
                    authenticated: ['AuthenticationService', function (AuthenticationService) {
                        return AuthenticationService.authenticationStatus();
                    }]
                }
            })
            .state('passwordChange',
            {
                url: '/passwordChange',
                controller: 'PasswordChangeController',
                templateUrl: '/views/authentication/passwordchange.html',
                resolve: {
                    authenticated: ['AuthenticationService', function (AuthenticationService) {
                        return AuthenticationService.authenticationStatus();
                    }]
                }
            })
            .state('authRequired',
            {
                url: '/authRequired',
                controller: 'AuthRequiredController',
                templateUrl: '/views/authentication/authrequired.html',
                resolve: {
                    authenticated: ['AuthenticationService', function (AuthenticationService) {
                        return AuthenticationService.authenticationStatus();
                    }]
                }
            })
            .state('restricted',
            {
                url: '/restricted',
                controller: 'RestrictedController',
                templateUrl: '/views/authentication/restricted.html',
                resolve: {
                    authenticated: ['AuthenticationService', function (AuthenticationService) {
                        return AuthenticationService.authenticationStatus();
                    }]
                }
            });
    }
}

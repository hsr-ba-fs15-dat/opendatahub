/// <reference path='../all.d.ts' />

module odh.auth {
    'use strict';
    angular
        .module(
        'openDataHub.auth', [
            'ngCookies',
            'ngSanitize',
            'ngRoute',
            'satellizer'
        ]
    ).config(($stateProvider:ng.ui.IStateProvider, $authProvider) => {
            $authProvider.authorizationPrefix = 'jwt';
            $authProvider.facebook({
                url: '',
                clientId: ''
            });
            $authProvider.github({
                url: '',
                clientId: ''
            });
            $stateProvider
                .state('login', {
                    url: '/login',
                    controller: 'LoginController as lc',
                    templateUrl: 'views/authentication/login.html',
                    resolve: {
                        authenticated: ['$auth', function ($auth) {
                            return $auth.isAuthenticated();
                        }]
                    }
                })
                .state('userProfile', {
                    url: '/userProfile',
                    controller: 'UserProfileController as up',
                    templateUrl: '/views/authentication/userprofile.html'
                })
                .state('logout', {
                    url: '/logout',
                    controller: 'LogoutController',
                    templateUrl: '/views/authentication/logout.html',
                    resolve: {
                        authenticated: ['$auth', function ($auth) {
                            return $auth.isAuthenticated();
                        }]
                    }
                });

        })

        .run(run);


    function run(AppConfig:odh.IAppConfig, satellizerConfig:any, UrlService:odh.utils.UrlService) {
        AppConfig.then((config) => {
            satellizerConfig.providers.github.url = UrlService.get('auth/social');
            satellizerConfig.providers.facebook.clientId = config.FACEBOOK_PUBLIC;
            satellizerConfig.providers.github.clientId = config.GITHUB_PUBLIC;
            satellizerConfig.providers.facebook.url = UrlService.get('auth/social');
        });
    }

    run.$inject = ['AppConfig', 'satellizer.config', 'UrlService'];
}

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
            'openDataHub.utils',
            'openDataHub.main'
        ])

        .config(($stateProvider:ng.ui.IStateProvider, $locationProvider:ng.ILocationProvider) => {
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
                });
        })
        .run(($http:ng.IHttpService) => {
            $http.defaults.xsrfHeaderName = 'X-CSRFToken';
            $http.defaults.xsrfCookieName = 'csrftoken';
        });

}

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
            'ui.bootstrap',
            'ui.grid',
            'openDataHub.auth',
            'openDataHub.utils',
            'openDataHub.main'
        ])

        .config(($stateProvider:ng.ui.IStateProvider, $locationProvider:ng.ILocationProvider,
                 UrlServiceProvider:odh.utils.UrlService) => {

            (<any>$).material.init();

            UrlServiceProvider.setApiPrefix('/api/v1/');

            $stateProvider
                .state('main', {
                    url: '/',
                    templateUrl: 'views/main.html'
                })
                .state('about', {
                    url: '/',
                    templateUrl: 'views/about.html'
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
                }).state('documents', {
                    url: '/document',
                    controller: 'DocumentListController as docs',
                    templateUrl: 'views/document.list.html'
                }).state('document', {
                    url: '/document/{id}',
                    controller: 'DocumentDetailController as doc',
                    templateUrl: 'views/document.detail.html',
                    params: {
                        'id': 0
                    }
                });
        })
        .run(($http:ng.IHttpService) => {
            $http.defaults.xsrfHeaderName = 'X-CSRFToken';
            $http.defaults.xsrfCookieName = 'csrftoken';
        });
}

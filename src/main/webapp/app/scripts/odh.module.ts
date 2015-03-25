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
            'restangular',
            'openDataHub.auth',
            'openDataHub.utils',
            'openDataHub.main'
        ])

        .config(($stateProvider:ng.ui.IStateProvider, $urlRouterProvider:ng.ui.IUrlRouterProvider,
                 UrlServiceProvider:odh.utils.UrlService, paginationConfig:ng.ui.bootstrap.IPaginationConfig,
                 RestangularProvider:restangular.IProvider) => {

            (<any>$).material.init();

            paginationConfig.firstText = 'Erste';
            paginationConfig.lastText = 'Letzte';
            paginationConfig.nextText = 'Nächste';
            paginationConfig.previousText = 'Zurück';


            RestangularProvider.setBaseUrl('/api/v1/');

            RestangularProvider.addResponseInterceptor(function (data, operation/*, what, url, response, deferred*/) {
                var extractedData;
                if (operation === 'getList' && data.results) {
                    extractedData = data.results;
                    var meta = angular.copy(data);
                    delete data.results;
                    extractedData.meta = meta;
                } else {
                    extractedData = data;
                }
                return extractedData;
            });

            UrlServiceProvider.setApiPrefix('/api/v1/');

            $urlRouterProvider.otherwise('/');

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
                })
                .state('documents', {
                    url: '/document',
                    controller: 'DocumentListController as docs',
                    templateUrl: 'views/document.list.html'
                })
                .state('document', {
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

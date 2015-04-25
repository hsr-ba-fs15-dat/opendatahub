/// <reference path='all.d.ts' />


module openDataHub {
    'use strict';
    angular
        .module('openDataHub', [
            'ngAnimate',
            'ngAria',
            'ngCookies',
            'ngMessages',
            'ngSanitize',
            'ngTouch',
            'ngTable',
            'ui.router',
            'ui.utils',
            'ui.select',
            'ui.bootstrap',
            'ui.grid',
            'ui.ace',
            'restangular',
            'truncate',
            'angularMoment',
            'openDataHub.auth',
            'openDataHub.utils',
            'openDataHub.main'
        ])

        .config(($stateProvider:ng.ui.IStateProvider, $urlRouterProvider:ng.ui.IUrlRouterProvider,
                 UrlServiceProvider:odh.utils.UrlService, paginationConfig:ng.ui.bootstrap.IPaginationConfig,
                 RestangularProvider:restangular.IProvider, $httpProvider:ng.IHttpProvider) => {

            (<any>$).material.init();

            paginationConfig.firstText = 'Erste';
            paginationConfig.lastText = 'Letzte';
            paginationConfig.nextText = 'Nächste';
            paginationConfig.previousText = 'Zurück';

            // django request.is_ajax() compatibility
            $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

            RestangularProvider.setBaseUrl('/api/v1/');
            RestangularProvider.setRequestSuffix('/');
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
                })
                .state('console', {
                    url: '/console',
                    controller: 'OdhQLConsoleController as vm',
                    templateUrl: 'views/odhql-console.html'
                })
                .state('transformation', {
                    abstract: true,
                    url: '/transformation',
                    templateUrl: 'views/transformation.html',
                    controller: 'TransformationController'

                })
                .state('transformation.create', {
                    url: '/create',
                    templateUrl: 'views/transformation.create.html',
                    controller: 'TransformationCreateController as vm'
                })
                .state('transformation.list', {
                    url: '/list',
                    templateUrl: 'views/transformation.list.html',
                    controller: 'TransformationListController as vm'
                })
                .state('transformation.detail', {
                    url: '/detail/{id}',
                    templateUrl: 'views/transformation.detail.html',
                    controller: 'TransformationDetailController as vm'

                }
            )
            ;
        })
        .run(($http:ng.IHttpService, $window:ng.IWindowService, amMoment) => {
            $http.defaults.xsrfHeaderName = 'X-CSRFToken';
            $http.defaults.xsrfCookieName = 'csrftoken';


            amMoment.changeLocale('de');
        });
}

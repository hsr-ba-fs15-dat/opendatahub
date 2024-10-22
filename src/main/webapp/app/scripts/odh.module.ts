/// <reference path='all.d.ts' />


module odh {
    'use strict';
    /**
     * configures the odh module
     */
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
            'ui.ace',
            'restangular',
            'truncate',
            'duScroll',
            'hljs',
            'angularMoment',
            'openDataHub.auth',
            'openDataHub.utils',
            'openDataHub.main'
        ])

        .config(($stateProvider:ng.ui.IStateProvider, $urlRouterProvider:ng.ui.IUrlRouterProvider,
                 UrlServiceProvider:odh.utils.UrlService, paginationConfig:ng.ui.bootstrap.IPaginationConfig,
                 RestangularProvider:restangular.IProvider, $httpProvider:ng.IHttpProvider, $provide,
                 hljsServiceProvider:any) => {

            var API_PREFIX = '/api/v1/';
            hljsServiceProvider.setOptions({
                // replace tab with 4 spaces
                tabReplace: '    '
            });
            $provide.decorator('$exceptionHandler', ['$delegate', '$injector', function ($delegate, $injector) {
                return function (exception, cause) {
                    var $http:ng.IHttpService = $injector.get('$http');
                    var UrlService:odh.utils.UrlService = $injector.get('UrlService');
                    var stacktrace = (<any>window).printStackTrace({e: exception});
                    var message = exception.message;
                    var url = (<any>window).location.href;

                    $http.post(UrlService.get('error_handler'), {
                        stracktrace: stacktrace.join('\n'),
                        message: message,
                        url: url,
                        cause: cause || ''
                    });

                    $delegate(exception, cause);
                };
            }]);


            (<any>$).material.init();

            paginationConfig.firstText = 'Erste';
            paginationConfig.lastText = 'Letzte';
            paginationConfig.nextText = 'Nächste';
            paginationConfig.previousText = 'Zurück';

            // django request.is_ajax() compatibility
            $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
            $httpProvider.interceptors.push('WarningHttpInterceptor');

            RestangularProvider.setBaseUrl(API_PREFIX);
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

            UrlServiceProvider.setApiPrefix(API_PREFIX);

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
                .state('packages', {
                    url: '/packages',
                    controller: 'PackageListController as docs',
                    templateUrl: 'views/package.list.html'
                })
                .state('document', {
                    url: '/document/{id:int}',
                    controller: 'DocumentDetailController as doc',
                    templateUrl: 'views/document.detail.html'
                })
                .state('odhql-help', {
                    url: '/transformation/help',
                    templateUrl: 'views/odhql-help.html'
                })
                .state('transformation-create', {
                    url: '/transformation/create?loadTransformation',
                    templateUrl: 'views/transformation.create.html'
                })
                .state('transformation-detail', {
                    url: '/transformation/{id:int}',
                    templateUrl: 'views/transformation.detail.html'
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

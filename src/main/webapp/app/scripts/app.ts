/// <reference path='all.d.ts' />

//(function () {
//    'use strict';
//
//    angular
//        .module('openDataHub', [
//            //'ngAnimate',
//            //'ngAria',
//            //'ngCookies',
//            //'ngMessages',
//            //'ngResource',
//            //'ngSanitize',
//            //'ngTouch',
//            //'ui.router',
//            //'ui.utils',
//            //'ui.select',
//            'ngToast',
//            'openDataHub.config',
//            'openDataHub.routes',
//            'openDataHub.auth',
//        ]);
//
//    angular
//
//    angular
//        .module('openDataHub.routes', ['ui.router']);
//    angular
//        .module('openDataHub')
//        .run(run);
//
//    run.$inject = ['$http'];
//
//    /**
//     * @name run
//     * @desc Update xsrf $http headers to align with Django's defaults
//     */
//    function
//})();
module openDataHub {
    'use strict';
    var openDataHub = angular
        .module('openDataHub', [
            //'ngAnimate',
            //'ngAria',
            //'ngCookies',
            //'ngMessages',
            //'ngResource',
            //'ngSanitize',
            //'ngTouch',
            //'ui.router',
            //'ui.utils',
            //'ui.select',
            'ngToast',
            'openDataHub.config',
            'openDataHub.routes',
            'openDataHub.auth',
        ]);

    var openDataConfig = angular
        .module('openDataHub.config', []);

    var openDataRoutes = angular
        .module('openDataHub.routes', ['ui.router']);

    angular
        .module('openDataHub')
        .config(config)
        .run(run);

    function run($http) {
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
    }

    function config ($stateProvider:ng.ui.IStateProvider){
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
            });

        }


}





//var app = angular
//    .module('opendatahubApp', [
//        'ngAnimate',
//        'ngAria',
//        'ngCookies',
//        'ngMessages',
//        'ngResource',
//        'ngSanitize',
//        'ngTouch',
//        'ui.router',
//        'ui.utils',
//        'ui.select',
//        'ngToast',
//        'opendatahubApp.authentication',
//    ])
//    .config(function ($stateProvider:ng.ui.IStateProvider, $urlRouterProvider:ng.ui.IUrlRouterProvider, ngToastProvider) {
//
//        // Toast config
//        ngToastProvider.configure({
//            horizontalPosition: 'center'
//        });
//
//        $urlRouterProvider.otherwise('/');
//
//        $stateProvider
//            .state('main', {
//                url: '/',
//                templateUrl: 'views/main.html'
//            })
//            .state('offer', {
//                controller: 'OfferCtrl',
//                templateUrl: 'views/offer.html',
//                controllerAs: 'vm'
//            })
//            .state('about', {
//                controller: 'AboutCtrl',
//                templateUrl: 'views/about.html'
//            })
//            .state('register', {
//                url: '/register',
//                controller: 'RegisterController as vm',
//                templateUrl: '/views/authentication/register.html'
//            })
//            .state('login', {
//                url: '/login',
//                controller: 'LoginController as vm',
//                templateUrl: '/views/authentication/login.html'
//            })
//
//        ;
//    });

//run(run);
//
//run.$inject = ['$http'];
//
///**
// * @name run
// * @desc Update xsrf $http headers to align with Django's defaults
// */
//function run($http) {
//    $http.defaults.xsrfHeaderName = 'X-CSRFToken';
//    $http.defaults.xsrfCookieName = 'csrftoken';
//}
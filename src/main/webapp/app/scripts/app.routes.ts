/// <reference path='../../typings/tsd.d.ts' />
(function () {
  'use strict';

  angular
    .module('openDataHub.routes')
    .config(config);

  config.$inject = ['$stateProvider'];

  function config($stateProvider) {
    //$routeProvider.when('/', {
    //  controller: 'IndexController',
    //  controllerAs: 'vm',
    //  templateUrl: '/static/templates/static/index.html'
    //}).when('/login', {
    //  controller: 'LoginController',
    //  controllerAs: 'vm',
    //  templateUrl: '/static/templates/static/login.html'
    //}).when('/register', {
    //  controller: 'RegisterController',
    //  controllerAs: 'vm',
    //  templateUrl: '/static/templates/static/register.html'
    //});

      $stateProvider
            //.state('main', {
            //    url: '/',
            //    templateUrl: 'views/main.html'
            //})
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
})();
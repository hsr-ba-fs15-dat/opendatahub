/// <reference path='../../typings/tsd.d.ts' />
(function () {
  'use strict';

  angular
    .module('openDataHub.config')
    .config(config);

  config.$inject = ['$locationProvider'];

  /**
  * @name config
  * @desc Enable HTML5 routing
  */
  function config($locationProvider) {

    $locationProvider.hashPrefix('!');
  }
})();
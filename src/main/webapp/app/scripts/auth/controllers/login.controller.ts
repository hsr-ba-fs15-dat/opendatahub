/// <reference path='../../../../typings/tsd.d.ts' />
/**
* LoginController
* @namespace openDataHub.auth.controllers
*/
(function () {
  'use strict';

  angular
    .module('openDataHub.auth.controllers')
    .controller('LoginController', LoginController);

  LoginController.$inject = ['$location', '$scope', 'Authentication'];

  /**
  * @namespace LoginController
  */
  function LoginController($location, $scope, Authentication) {
    var vm = this;

    vm.login = login;

    activate();

    /**
    * @name activate
    * @desc Actions to be performed when this controller is instantiated
    * @memberOf openDataHub.auth.controllers.LoginController
    */
    function activate() {
      // If the user is authenticated, they should not be here.
      if (Authentication.isAuthenticated()) {
        $location.url('/');
      }
    }

    /**
    * @name login
    * @desc Log the user in
    * @memberOf openDataHub.auth.controllers.LoginController
    */
    function login() {
      Authentication.login(vm.email, vm.password);
    }
  }
})();
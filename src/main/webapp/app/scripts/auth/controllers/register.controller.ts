/// <reference path='../../../../typings/tsd.d.ts' />

/**
 * Register controller
 * @namespace openDataHub.auth.controllers
 */
(function () {
    'use strict';

    angular
        .module('openDataHub.auth.controllers')
        .controller('RegisterController', RegisterController);

    RegisterController.$inject = ['$location', '$scope', 'Authentication'];

    /**
     * @namespace RegisterController
     */
    function RegisterController($location, $scope, Authentication) {
        var vm = this;
        activate();

        /**
         * @name activate
         * @desc Actions to be performed when this controller is instantiated
         * @memberOf openDataHub.auth.controllers.RegisterController
         */
        function activate() {
            // If the user is authenticated, they should not be here.
            if (Authentication.isAuthenticated()) {
                $location.url('/');
            }
        }

        vm.register = register;

        /**
         * @name register
         * @desc Register a new user
         * @memberOf openDataHub.auth.controllers.RegisterController
         */
        function register() {
            Authentication.register(vm.email, vm.password, vm.username);
        }
    }
})();
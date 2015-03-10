/// <reference path='../../../../typings/tsd.d.ts' />

/**
 * Register controller
 * @namespace openDataHub.auth.controllers
 */
module openDataHub {
    'use strict';
    export class RegisterController {

        //RegisterController.$inject = ['$location', '$scope', 'Authentication'];
        public email;
        public password;
        public username;

        /**
         * @namespace RegisterController
         */
        constructor(private $location, private $scope, private Authentication) {
            this.activate();


        }

        /**
         * @name activate
         * @desc Actions to be performed when this controller is instantiated
         * @memberOf openDataHub.auth.controllers.RegisterController
         */
        activate() {
            // If the user is authenticated, they should not be here.
            if (this.Authentication.isAuthenticated()) {
                this.$location.url('/');
            }
        }

        /**
         * @name register
         * @desc Register a new user
         * @memberOf openDataHub.auth.controllers.RegisterController
         */

        register() {
            this.Authentication.register(this.email, this.password, this.username);
        }
    }
}
;

angular.module('openDataHub').controller('RegisterController',openDataHub.RegisterController);

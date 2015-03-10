/// <reference path='../../all.d.ts' />

/**
 * Register controller
 * @namespace openDataHub.auth.controllers
 */
module odh {
    'use strict';

    export class RegisterController {

        public email:string;
        public password:string;
        public username:string;

        /**
         * @namespace RegisterController
         */
        constructor(private $location:ng.ILocationService, private $scope:ng.IScope, private AuthenticationService:odh.AuthenticationService) {
            this.activate();

        }

        /**
         * @name activate
         * @desc Actions to be performed when this controller is instantiated
         * @memberOf openDataHub.auth.controllers.RegisterController
         */
        activate() {
            // If the user is authenticated, they should not be here.
            if (this.AuthenticationService.isAuthenticated()) {
                this.$location.url('/');
            }
        }

        /**
         * @name register
         * @desc Register a new user
         * @memberOf openDataHub.auth.controllers.RegisterController
         */

        register() {
            this.AuthenticationService.register(this.email, this.password, this.username);
        }
    }
    angular.module('openDataHub').controller('RegisterController', RegisterController);
}



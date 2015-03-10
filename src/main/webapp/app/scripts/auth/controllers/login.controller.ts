/// <reference path='../../all.d.ts' />

/**
 * LoginController
 * @namespace openDataHub.auth.controllers
 */
module odg {
    'use strict';

    class LoginController {
        public email:string;
        public password:string;
        /**
         * @namespace LoginController
         *
         */
        constructor(private $location, private $scope, private AuthenticationService:odh.AuthenticationService) {
            this.activate();

        }

        /**
         * @name activate
         * @desc Actions to be performed when this controller is instantiated
         * @memberOf openDataHub.auth.controllers.LoginController
         */
        activate() {
            // If the user is authenticated, they should not be here.
            if (this.AuthenticationService.isAuthenticated()) {
                this.$location.url('/');
            }
        }

        /**
         * @name login
         * @desc Log the user in
         * @memberOf openDataHub.auth.controllers.LoginController
         */
        login() {
            this.AuthenticationService.login(this.email, this.password);
        }
    }
    angular.module('openDataHub').controller('LoginController', LoginController);
}

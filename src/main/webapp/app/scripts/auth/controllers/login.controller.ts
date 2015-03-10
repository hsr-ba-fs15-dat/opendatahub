/// <reference path='../../../../typings/tsd.d.ts' />
/**
 * LoginController
 * @namespace openDataHub.auth.controllers
 */
module openDataHub {
    'use strict';

    export class LoginController {
        public email:string;
        public password:string;
        /**
         * @namespace LoginController
         *
         */
        constructor(private $location, private $scope, private Authentication) {
            this.activate();

        }

        /**
         * @name activate
         * @desc Actions to be performed when this controller is instantiated
         * @memberOf openDataHub.auth.controllers.LoginController
         */
        activate() {
            // If the user is authenticated, they should not be here.
            if (this.Authentication.isAuthenticated()) {
                this.$location.url('/');
            }
        }

        /**
         * @name login
         * @desc Log the user in
         * @memberOf openDataHub.auth.controllers.LoginController
         */
        login() {
            this.Authentication.login(this.email, this.password);
        }
    }
}
angular.module('openDataHub').controller('LoginController', openDataHub.LoginController);

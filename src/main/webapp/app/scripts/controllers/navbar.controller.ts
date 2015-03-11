/// <reference path='../all.d.ts' />

/**
 * NavbarController
 * @namespace openDataHub.controllers
 */
module openDataHub {
    'use strict';
    class NavBarController {
        public email:string;
        public password:string;

        /**
         * @namespace LoginController
         *
         */
        constructor(private $location, private $scope, private AuthenticationService) {
            this.activate();
        }

        /**
         * @name activate
         * @desc Actions to be performed when this controller is instantiated
         * @memberOf openDataHub.LoginController
         */
        private activate() {

        }

        /**
         //    * @name logout
         //    * @desc Log the user out
         //    * @memberOf openDataHub.NavBarController
         //    */
        logout() {
            this.AuthenticationService.logout();
        }
        isAuthenticated()
        {
            return this.AuthenticationService.isAuthenticated();
        }
        getAuthenticatedAccount()
        {
            return this.AuthenticationService.getAuthenticatedAccount();
        }
    }
    angular.module('openDataHub').controller('NavBarController', NavBarController);
}
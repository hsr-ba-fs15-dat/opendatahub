/// <reference path='../all.d.ts' />


module odh {
    'use strict';

    class NavBarController {

        public email:string;
        public password:string;

        constructor(private $location:ng.ILocationService,
                    private AuthenticationService:odh.auth.AuthenticationService) {

        }

        logout() {
            this.AuthenticationService.logout();
        }

        isAuthenticated() {
            return this.AuthenticationService.isAuthenticated();
        }

        getAuthenticatedAccount() {
            return this.AuthenticationService.getAuthenticatedAccount();
        }
    }

    angular.module('openDataHub').controller('NavBarController', NavBarController);
}

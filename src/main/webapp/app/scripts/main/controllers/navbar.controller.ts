/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';
    /**
     * provides the navbar
     * - shows username if logged in
     * - checks if authenticated
     * - logs out the user
     */
    class NavBarController {

        constructor(private UserService:auth.UserService) {

        }

        public isAuthenticated() {
            return this.UserService.isAuthenticated();
        }

        public loginName():string {
            var username = null;
            if (this.isAuthenticated()) {
                username = this.UserService.getPayload().username;
            }
            return username;
        }

        public logout() {
            this.UserService.logout();
        }
    }

    angular.module('openDataHub.main').controller('NavBarController', NavBarController);
}

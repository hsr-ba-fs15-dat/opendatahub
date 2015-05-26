/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    class NavBarController {

        constructor(private $auth) {

        }

        public isAuthenticated() {
            return this.$auth.isAuthenticated();
        }

        public loginName() {
            if (this.isAuthenticated()) {
                return this.$auth.getPayload().username;
            }
            return false;
        }

        public logout() {
            this.$auth.logout();
        }
    }

    angular.module('openDataHub.main').controller('NavBarController', NavBarController);
}

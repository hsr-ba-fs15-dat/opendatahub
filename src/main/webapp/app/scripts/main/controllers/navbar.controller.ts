/// <reference path='../../all.d.ts' />


module odh {
    'use strict';

    class NavBarController {

        public email:string;
        public password:string;

        constructor(private $auth) {

        }

        public isAuthenticated() {
            return this.$auth.isAuthenticated();
        }

        public logout() {
            this.$auth.logout();
        }
    }

    angular.module('openDataHub.main').controller('NavBarController', NavBarController);
}

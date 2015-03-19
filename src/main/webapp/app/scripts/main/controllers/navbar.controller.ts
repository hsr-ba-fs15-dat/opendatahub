/// <reference path='../../all.d.ts' />


module odh {
    'use strict';

    class NavBarController {

        public email:string;
        public password:string;

        constructor(private AuthenticationService:odh.auth.AuthenticationService) {

        }

        public isAuthenticated() {
            return this.AuthenticationService.isAuthed();
        }

        public logout() {
            this.AuthenticationService.logout();
        }
    }

    angular.module('openDataHub.main').controller('NavBarController', NavBarController);
}

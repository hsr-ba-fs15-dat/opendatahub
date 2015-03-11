/// <reference path='../../all.d.ts' />


module odh {

    'use strict';

    export class RegisterController {

        public email:string;
        public password:string;
        public username:string;

        constructor(private $state, private AuthenticationService:odh.auth.AuthenticationService) {
            this.activate();
        }

        /**
         * Register a new user
         */
        public register() {
            this.AuthenticationService.register(this.email, this.password, this.username);
        }

        /**
         * Actions to be performed when this controller is instantiated
         */
        private activate() {
            // if the user is authenticated, they should not be here.
            if (this.AuthenticationService.isAuthenticated()) {
                this.$state.go('main');
            }
        }

    }
    angular.module('openDataHub').controller('RegisterController', RegisterController);

}

/// <reference path='../../all.d.ts' />


module odh {
    'use strict';

    class LoginController {
        public email:string;
        public password:string;

        constructor(private $state, private AuthenticationService:odh.auth.AuthenticationService) {
            this.activate();
        }

        /**
         * Log the user in
         */
        public login() {
            this.AuthenticationService.login(this.email, this.password);
        }

        private activate() {
            // if the user is authenticated, they should not be here.
            if (this.AuthenticationService.isAuthenticated()) {
                this.$state.go('main');
            }
        }
    }
    angular.module('openDataHub').controller('LoginController', LoginController);

}

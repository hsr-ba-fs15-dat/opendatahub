/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class LoginController {

        public authenticating = false;

        constructor(private UserService:UserService,
                    private $auth) {
        }

        public authenticate(provider) {
            this.authenticating = true;
            this.$auth.authenticate(provider, {backend: provider});
        }

        public logout() {
            this.$auth.logout();
        }

    }
    angular.module('openDataHub.auth').controller('LoginController', LoginController);
}

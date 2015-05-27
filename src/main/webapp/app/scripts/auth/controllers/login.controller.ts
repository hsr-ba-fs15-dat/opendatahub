/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';
    /**
     * responsible for logging the user in and connect the social profile to the opendatahub profile.
     * - provides authentication
     * - provides logout
     */
    class LoginController {

        public authenticating = false;


        constructor(private UserService:auth.UserService, private ToastService:utils.ToastService) {
        }

        public authenticate(provider) {
            this.authenticating = true;
            this.UserService.authenticate(provider, {backend: provider}).catch(() => {
                this.ToastService.failure('Der Login ist fehlgeschlagen');
                this.authenticating = false;
            });
        }

        public logout() {
            this.UserService.logout();
        }

    }
    angular.module('openDataHub.auth').controller('LoginController', LoginController);
}

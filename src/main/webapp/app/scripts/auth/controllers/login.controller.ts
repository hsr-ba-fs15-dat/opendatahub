/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class LoginController {

        public authenticating = false;

        constructor(private $auth, private ToastService:utils.ToastService) {
        }

        public authenticate(provider) {
            this.authenticating = true;
            this.$auth.authenticate(provider, {backend: provider}).catch(() => {
                this.ToastService.failure('Der Login ist fehlgeschlagen');
                this.authenticating = false;
            });
        }

        public logout() {
            this.$auth.logout();
        }

    }
    angular.module('openDataHub.auth').controller('LoginController', LoginController);
}

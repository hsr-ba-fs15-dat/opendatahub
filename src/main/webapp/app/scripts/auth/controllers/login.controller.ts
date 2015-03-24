/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class LoginController {


        constructor(private AuthenticationService:AuthenticationService,
                    private UserService:UserService,
                    private $auth) {
        }

        public authenticate(provider) {
            this.$auth.authenticate(provider, {backend: provider}).then(
                (data) => {
                    this.UserService.login(data).then(() => {

                        console.log(this.AuthenticationService.isAuthed());

                    });
                });
        }

        public logout() {
            this.$auth.logout();
        }


    }
    angular.module('openDataHub.auth').controller('LoginController', LoginController);
}

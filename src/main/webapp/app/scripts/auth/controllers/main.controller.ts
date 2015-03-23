/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class MainController {
        public  message;
        public socialToken;

        constructor(private UserService:UserService,
                    private AuthenticationService:AuthenticationService) {
            // controller init
        }


        public login() {
            this.UserService.login(this.socialToken, 'facebook')
                .then(this.handleRequest, this.handleRequest);
        }

        public logout() {
            this.AuthenticationService.logout();
        }

        public isAuthed() {
            return this.AuthenticationService.isAuthed();
        }

        private  handleRequest(res) {
            var token = res.data ? res.data.token : null;
            if (token) {
                console.log('JWT:', token);
            }
            this.message = res.data.message;
        }

    }
    angular.module('openDataHub.auth').controller('MainController', MainController);
}

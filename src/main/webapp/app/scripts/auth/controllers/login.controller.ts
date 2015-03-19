/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class LoginController {


        constructor(private FaceBookService:FaceBookService,
                    private AuthenticationService:AuthenticationService,
                    private UserService: UserService
            ) {
            // controller init
        }

        public login() {
            this.FaceBookService.login().then((response) => {
                // this is where we'll contact backend. for now just log response
                console.log('facebook');
                var reqObj = {
                    access_token: response.authResponse.accessToken
                };
                this.UserService.login(reqObj).then(() => {

                    console.log (this.AuthenticationService.isAuthed());
                    // this.$location.path('/userProfile');

                });
            });
        }
    }
    angular.module('openDataHub.auth').controller('LoginController', LoginController);
}

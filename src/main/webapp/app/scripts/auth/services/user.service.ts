/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    export class UserService {

        public temp:{};

        constructor(private $http:ng.IHttpService, public API, private AuthenticationService:AuthenticationService,
                    private $auth) {

        }

        public authenticate(provider) {
            this.$auth.authenticate(provider);
        }

        public login(socialToken, provider = 'facebook') {
            return this.$http.post(this.API + 'auth/social/', {
                access_token: socialToken.access_token,
                backend: provider
            }).then((data:any) => {
                var token = data.data.token;
                this.AuthenticationService.saveToken(token);
            });
        }

        public profile() {
            return this.$http.get(this.API + 'auth/' + 'user/');
        }

    }
    angular.module('openDataHub.auth').service('UserService', UserService);
}

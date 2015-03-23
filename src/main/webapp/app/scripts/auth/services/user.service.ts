/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    export class UserService {

        public temp:{};

        constructor(private $http:ng.IHttpService, public API, private AuthenticationService:AuthenticationService) {

        }

        public login(socialToken, provider = 'facebook') {
            return this.$http.post(this.API + provider + '/', {
                access_token: socialToken.access_token,
                backend: provider
            }).then((data:any) => {

                console.log(data);
                console.log(data.data.token);
                var token = data.data.token;
                this.AuthenticationService.saveToken(token);

            });
        }

        public profile() {
            return this.$http.get(this.API + 'user/');
        }

    }
    angular.module('openDataHub.auth').service('UserService', UserService);
}

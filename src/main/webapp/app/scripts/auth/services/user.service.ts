/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    export class UserService {

        public temp:{};

        constructor(private $http:ng.IHttpService, private $auth, private UrlService:odh.utils.UrlService) {

        }

        public authenticate(provider) {
            this.$auth.authenticate(provider);
        }

        public profile() {
            return this.$http.get(this.UrlService.get('auth/user'));
        }

        public isAuthenticated() {
            return this.$auth.isAuthenticated();
        }

    }
    angular.module('openDataHub.auth').service('UserService', UserService);
}

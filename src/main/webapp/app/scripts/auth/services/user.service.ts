/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    export class UserService {

        public temp:{};

        constructor(private $http:ng.IHttpService,
                    private $auth) {

        }

        public authenticate(provider) {
            this.$auth.authenticate(provider);
        }

        public profile() {
            return this.$http.get('/api/v1/auth/' + 'user/');
        }

        public isAuthenticated() {
            return this.$auth.isAuthenticated();
        }

    }
    angular.module('openDataHub.auth').service('UserService', UserService);
}

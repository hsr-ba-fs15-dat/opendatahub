/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';
    /**
     * provides an interface for the used methods of the [satellizer]{@link https://github.com/sahat/satellizer}
     * package.
     */
    export interface IAuth {
        authenticate(provider, args):ng.IPromise<any>;
        isAuthenticated():boolean;
        logout():void;
    }
    /**
     * responsible for handling the user authentication.
     * - provides profile
     * - provides authentication
     * - provides authentication checks
     * - provides logout
     */
    export class UserService {

        constructor(private $http:ng.IHttpService, private $auth:auth.IAuth, private UrlService:odh.utils.UrlService) {

        }

        public authenticate(provider, args = null) {
            return this.$auth.authenticate(provider, args);
        }

        public profile() {
            return this.$http.get(this.UrlService.get('auth/user'));
        }

        public isAuthenticated() {
            return this.$auth.isAuthenticated();
        }

        public logout() {
            return this.$auth.logout();
        }

    }
    angular.module('openDataHub.auth').service('UserService', UserService);
}

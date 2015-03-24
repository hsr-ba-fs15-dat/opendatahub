/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    export class AuthenticationService {
        private $window:ng.IWindowService;

        /* @ngInject */
        public $get($window:ng.IWindowService) {
            this.$window = $window;
            return this;
        }


        public parseJwt(token) {
            var base64Url = token.split('.')[1];
            var base64 = base64Url.replace('-', '+').replace('_', '/');
            return JSON.parse(this.$window.atob(base64));
        }

        public saveToken(token) {
            this.$window.localStorage.setItem('jwtToken', token);
        }

        public getToken() {
            return this.$window.localStorage.getItem('jwtToken');
        }

        public isAuthed() {
            var token = this.getToken();
            if (token) {
                var params = this.parseJwt(token);
                return Math.round(new Date().getTime() / 1000) <= params.exp;
            } else {
                return false;
            }
        }

        public logout() {
            this.$window.localStorage.removeItem('jwtToken');
        }
    }

    export class AuthenticationInterceptor {


        constructor(private AuthenticationServiceProvider:AuthenticationService, private API) {
        }


        public response = (res) => {
            if (res.config.url.indexOf(this.API) === 0 && res.data.token) {
                this.AuthenticationServiceProvider.saveToken(res.data.token);
            }

            return res;
        };

        public request = (config) => {
            var token = this.AuthenticationServiceProvider.getToken();
            if (config.url.indexOf(this.API) === 0 && token) {
                config.headers.Authorization = 'jwt ' + token;
            }

            return config;
        };
        /* @ngInject */
        public static Factory(AuthenticationService:auth.AuthenticationService, API) {
            return new AuthenticationInterceptor(AuthenticationService, API);
        }
    }
    angular.module('openDataHub.auth').provider('AuthenticationService', AuthenticationService)
        .constant('API', '/api/v1/');
    angular.module('openDataHub').config(($httpProvider:ng.IHttpProvider) => {
                $httpProvider.interceptors.push(odh.auth.AuthenticationInterceptor.Factory);
    });
}


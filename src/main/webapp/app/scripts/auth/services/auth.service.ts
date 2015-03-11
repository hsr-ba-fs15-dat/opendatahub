/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    export class AuthenticationService {

        constructor(private $cookies, private $http:ng.IHttpService, private $state:ng.ui.IStateService,
                    private $log:ng.ILogService) {

        }

        /**
         * Try to register a new user
         * @param username The username entered by the user
         * @param password The password entered by the user
         * @param email The email entered by the user
         */
        public register(email, password, username):ng.IPromise<any> {
            return this.$http.post('/api/v1/accounts', {
                username: username,
                password: password,
                email: email
            }).then(data => {
                this.login(email, password);
            }).catch(data => {
                this.$log.error('Error while registering', data);
            });
        }

        /**
         * @name login
         * @desc Try to log in with email `email` and password `password`
         * @param {string} email The email entered by the user
         * @param {string} password The password entered by the user
         * @returns {Promise}
         * @memberOf openDataHub.auth.services.Authentication
         */
        public login(email, password) {
            return this.$http.post('/api/v1/auth/login', {
                email: email, password: password
            }).then(data => {
                this.setAuthenticatedAccount(data.data);
                this.$state.go('main');
            }).catch(() => {
                this.$log.error('Epic failure!');

            });
        }

        /**
         * @name getAuthenticatedAccount
         * @desc Return the currently authenticated account
         * @returns Account if authenticated, else `undefined`
         */
        public getAuthenticatedAccount():any;
        public getAuthenticatedAccount():void {
            if (!sessionStorage.getItem('user')) {
                return;
            }

            return JSON.parse(sessionStorage.getItem('user'));
        }

        /**
         * Check if the current user is authenticated
         * @returns True is user is authenticated, else false.
         * @memberOf openDataHub.auth.services.Authentication
         */
        public isAuthenticated():boolean {
            return !!sessionStorage.getItem('user');
        }

        /**
         * Delete the cookie where the user object is stored
         */
        public unauthenticate() {
            delete this.$cookies.authenticatedAccount;
            sessionStorage.removeItem('user');
        }

        /**
         * Try to log the user out
         */
        public logout():ng.IPromise<any> {
            return this.$http.post('/api/v1/auth/logout', {})
                .then(() => {
                    this.unauthenticate();
                    this.$state.go('main');
                }).catch(() => {
                    this.$log.error('Epic failure!');
                });
        }

        /**
         * Stringify the account object and store it in a cookie
         * @param account The account object to be stored
         */
        private setAuthenticatedAccount(account) {
            this.$cookies.authenticatedAccount = JSON.stringify(account);
            sessionStorage.setItem('user', JSON.stringify(account));
        }
    }
    angular.module('openDataHub').service('AuthenticationService', AuthenticationService);
}


/// <reference path='../../../../typings/tsd.d.ts' />
/**
 * Authentication
 * @namespace openDataHub.auth.services
 */
module openDataHub {
    'use strict';

    export class AuthenticationService {
        /* ngInject */
        constructor(private $cookies,
                    private $http, private $state:ng.ui.IStateService) {

        }

        /**
         * @name register
         * @desc Try to register a new user
         * @param {string} username The username entered by the user
         * @param {string} password The password entered by the user
         * @param {string} email The email entered by the user
         * @returns {Promise}
         * @memberOf openDataHub.auth.services.Authentication
         */
        register(email, password, username) {
            var that = this;
            return this.$http.post('/api/v1/accounts/', {
                username: username,
                password: password,
                email: email
            }).then(registerSuccessFn, registerErrorFn);

            /**
             * @name registerSuccessFn
             * @desc Log the new user in
             */
            function registerSuccessFn(data, status, headers, config) {
                that.login(email, password);
            }

            /**
             * @name registerErrorFn
             * @desc Log "Epic failure!" to the console
             */
            function registerErrorFn(data, status, headers, config) {
                console.error('Epic failure!');
            }
        }


        /**
         * @name login
         * @desc Try to log in with email `email` and password `password`
         * @param {string} email The email entered by the user
         * @param {string} password The password entered by the user
         * @returns {Promise}
         * @memberOf openDataHub.auth.services.Authentication
         */


        login(email, password) {
            var that = this;
            return this.$http.post('/api/v1/auth/login/', {
                email: email, password: password
            }).then(loginSuccessFn, loginErrorFn);
            /**
             * @name loginSuccessFn
             * @desc Set the authenticated account and redirect to index
             */
            function loginSuccessFn(data, status, headers, config) {
                that.setAuthenticatedAccount(data.data);
                that.$state.go('main');
            }

            /**
             * @name loginErrorFn
             * @desc Log "Epic failure!" to the console
             */
            function loginErrorFn(data, status, headers, config) {
                console.error('Epic failure!');
            }
        }

        /**
         * @name getAuthenticatedAccount
         * @desc Return the currently authenticated account
         * @returns {object|undefined} Account if authenticated, else `undefined`
         * @memberOf openDataHub.auth.services.Authentication
         */
        getAuthenticatedAccount() {
            if (!sessionStorage.getItem('user')) {
                return;
            }

            return JSON.parse(sessionStorage.getItem('user'));
        }


        /**
         * @name isAuthenticated
         * @desc Check if the current user is authenticated
         * @returns {boolean} True is user is authenticated, else false.
         * @memberOf openDataHub.auth.services.Authentication
         */
        isAuthenticated() {
            return !!sessionStorage.getItem('user');
        }


        /**
         * @name setAuthenticatedAccount
         * @desc Stringify the account object and store it in a cookie
         * @param {Object} account The account object to be stored
         * @returns {undefined}
         * @memberOf openDataHub.auth.services.Authentication
         */
        setAuthenticatedAccount(account) {
            this.$cookies['authenticatedAccount'] = JSON.stringify(account);
            sessionStorage.setItem('user',JSON.stringify(account));
        }

        /**
         * @name unauthenticate
         * @desc Delete the cookie where the user object is stored
         * @returns {undefined}
         * @memberOf openDataHub.auth.services.Authentication
         */
        unauthenticate() {
            delete this.$cookies.authenticatedAccount;
            sessionStorage.removeItem('user')
        }

        /**
         * @name logout
         * @desc Try to log the user out
         * @returns {Promise}
         * @memberOf openDataHub.auth.services.Authentication
         */
        logout() {
                        var that = this;

            return this.$http.post('/api/v1/auth/logout/')
                .then(logoutSuccessFn, logoutErrorFn);

            /**
             * @name logoutSuccessFn
             * @desc Unauthenticate and redirect to index with page reload
             */
            function logoutSuccessFn(data, status, headers, config) {
                that.unauthenticate();
                that.$state.go('main');
            }

            /**
             * @name logoutErrorFn
             * @desc Log "Epic failure!" to the console
             */
            function logoutErrorFn(data, status, headers, config) {
                console.error('Epic failure!');
            }
        }
    }
angular.module('openDataHub').service('AuthenticationService',AuthenticationService);

}


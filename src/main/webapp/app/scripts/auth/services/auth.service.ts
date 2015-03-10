/// <reference path='../../all.d.ts' />

/**
 * Authentication
 * @namespace openDataHub.auth.services
 */
module odh {
    'use strict';

    export class AuthenticationService {

        constructor(private $cookies:ng.cookies.ICookiesService,
                    private $http:ng.IHttpService, private $state:ng.ui.IStateService, private $log:ng.ILogService) {

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
            return this.$http.post('/api/v1/accounts/', {
                username: username,
                password: password,
                email: email
            }).then(data => {
                this.login(email, password);
            }).catch(data => {
                this.$log.error('Epic failure!');

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
        login(email, password) {
            return this.$http.post('/api/v1/auth/login/', {
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
         * @returns {object|undefined} Account if authenticated, else `undefined`
         * @memberOf openDataHub.auth.services.Authentication
         */
        getAuthenticatedAccount() {
            if (!this.$cookies['authenticatedAccount']) {
                return;
            }

            return JSON.parse(this.$cookies['authenticatedAccount']);
        }


        /**
         * @name isAuthenticated
         * @desc Check if the current user is authenticated
         * @returns {boolean} True is user is authenticated, else false.
         * @memberOf openDataHub.auth.services.Authentication
         */
        isAuthenticated() {
            return !!this.$cookies['authenticatedAccount'];
        }


        /**
         * @name setAuthenticatedAccount
         * @desc Stringify the account object and store it in a cookie
         * @param {Object} user The account object to be stored
         * @returns {undefined}
         * @memberOf openDataHub.auth.services.Authentication
         */
        setAuthenticatedAccount(account) {
            this.$cookies['authenticatedAccount'] = JSON.stringify(account);
        }

        /**
         * @name unauthenticate
         * @desc Delete the cookie where the user object is stored
         * @returns {undefined}
         * @memberOf openDataHub.auth.services.Authentication
         */
        unauthenticate() {
            delete this.$cookies['authenticatedAccount'];
        }

        /**
         * @name logout
         * @desc Try to log the user out
         * @returns {Promise}
         * @memberOf openDataHub.auth.services.Authentication
         */
        logout() {
            return this.$http.post('/api/v1/auth/logout/', {})
                .then(() => {
                    this.unauthenticate();
                    this.$state.go('main');
                }).catch(() => {
                    this.$log.error('Epic failure!');
                });
        }
    }
    angular.module('openDataHub').service('AuthenticationService', AuthenticationService);
}


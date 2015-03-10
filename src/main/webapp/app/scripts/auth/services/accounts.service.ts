/// <reference path='../../../../typings/tsd.d.ts' />
/**
 * Account
 * @namespace openDataHub.auth.services
 */
module openDataHub {
    'use strict';
    export class AccountService {
        public email:string;
        public password:string;

        /**
         * @namespace AccountService
         *
         */
        constructor(private $http) {
        }

        /**
         * @name destroy
         * @desc Destroys the account with username `username`
         * @param {string} username The username of the account to be destroyed
         * @returns {Promise}
         * @memberOf openDataHub.auth.services.AccountService
         */
        destroy(username) {
            return this.$http.delete('/api/v1/accounts/' + username + '/');
        }


        /**
         * @name get
         * @desc Gets the account with username `username`
         * @param {string} username The username of the account to get
         * @returns {Promise}
         * @memberOf openDataHub.auth.services.AccountService
         */
        get(username) {
            return this.$http.get('/api/v1/accounts/' + username + '/');
        }


        /**
         * @name update
         * @desc Update the account with username `username`
         * @param {string} username The username of the account to be updated
         * @param {Object} account The updated account model
         * @returns {Promise}
         * @memberOf openDataHub.auth.services.AccountService
         */
        update(username, account) {
            return this.$http.put('/api/v1/accounts/' + username + '/', account);
        }

    }
    angular.module('openDataHub').service('AccountService', AccountService);
}

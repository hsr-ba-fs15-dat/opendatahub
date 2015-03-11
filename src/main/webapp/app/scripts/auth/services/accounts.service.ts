/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    export class AccountService {
        public email:string;
        public password:string;

        constructor(private $http:ng.IHttpService) {

        }

        /**
         * Destroys the account with username `username`
         * @param username The username of the account to be destroyed
         */
        public destroy(username):ng.IHttpPromise<any> {
            return this.$http.delete('/api/v1/accounts/' + username);
        }

        /**
         * Gets the account with username `username`
         * @param  username The username of the account to get
         */
        public get(username):ng.IHttpPromise<any> {
            return this.$http.get('/api/v1/accounts/' + username);
        }

        /**
         * Update the account with username `username`
         * @param username The username of the account to be updated
         * @param account The updated account model
         */
        public update(username, account):ng.IHttpPromise<any> {
            return this.$http.put('/api/v1/accounts/' + username, account);
        }

    }
    angular.module('openDataHub.auth').service('AccountService', AccountService);
}

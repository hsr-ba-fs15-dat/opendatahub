/// <reference path='../../all.d.ts' />

/**
 * AccountSettingsController
 * @namespace openDataHub.auth.controllers
 */
module openDataHub {
    'use strict';
    class AccountSettingsController {

        /**
         * @namespace AccountSettingsController
         *
         */
        private account;

        constructor(private AuthenticationService:odh.AuthenticationService, private AccountService, private $state, private $stateParams) {
            this.activate();
        }

        /**
         * @name activate
         * @desc Actions to be performed when this controller is instantiated.
         * @memberOf openDataHub.auth.controllers.AccountSettingsController
         */
        activate() {
            var authenticatedAccount = this.AuthenticationService.getAuthenticatedAccount();
            var username = this.$stateParams.username;
            var that = this;
            // Redirect if not logged in
            if (!authenticatedAccount) {
                this.$state.go('main');

                //Snackbar.error('You are not authorized to view this page.');
                //TODO: Nice error Framework

            } else {
                // Redirect if logged in, but not the owner of this account.
                if (authenticatedAccount.username !== username) {
                    debugger;
                    this.$state.go('main');

                    //Snackbar.error('You are not authorized to view this page.');
                    //TODO: Nice error Framework

                }
            }

            this.AccountService.get(username).then(accountSuccessFn, accountErrorFn);

            /**
             * @name accountSuccessFn
             * @desc Update `account` for view
             */
            function accountSuccessFn(data, status, headers, config) {
                that.account = data.data;
            }

            /**
             * @name accountErrorFn
             * @desc Redirect to index
             */
            function accountErrorFn(data, status, headers, config) {

                this.$state.go('main');

                //Snackbar.error('That user does not exist.');

            }
        }


        /**
         * @name destroy
         * @desc Destroy this account
         * @memberOf openDataHub.auth.controllers.AccountSettingsController
         */
        destroy() {
            var that = this;
            this.AccountService.destroy(this.account.username).then(accountSuccessFn, accountErrorFn);

            /**
             * @name accountSuccessFn
             * @desc Redirect to index and display success snackbar
             */
            function accountSuccessFn(data, status, headers, config) {
                that.AuthenticationService.unauthenticate();
                that.$state.go('main');

                //Snackbar.show('Your account has been deleted.');
            }


            /**
             * @name accountErrorFn
             * @desc Display error
             */
            function accountErrorFn(data, status, headers, config) {
                //Snackbar.error(data.error);
            }
        }


        /**
         * @name update
         * @desc Update this account
         * @memberOf openDataHub.auth.controllers.AccountSettingsController
         */
        update() {
            var username = this.$stateParams.username;

            this.AccountService.update(username, this.account).then(accountSuccessFn, accountErrorFn);

            /**
             * @name accountSuccessFn
             * @desc Show success
             */
            function accountSuccessFn(data, status, headers, config) {
                //Snackbar.show('Your account has been updated.');
            }


            /**
             * @name accountErrorFn
             * @desc Show error
             */
            function accountErrorFn(data, status, headers, config) {
                //Snackbar.error(data.error);
            }
        }
    }
    angular.module('openDataHub').controller('AccountSettingsController', AccountSettingsController);

}
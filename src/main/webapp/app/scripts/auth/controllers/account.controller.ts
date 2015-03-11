/// <reference path='../../all.d.ts' />

/**
 * AccountSettingsController
 * @namespace openDataHub.auth.controllers
 */
module openDataHub {
    'use strict';
    class AccountController {
        /**
         * @namespace AccountController
         *
         */
        private account;
        /* ngInject */
        constructor(private $location, private AccountService, private $stateParams) {
            this.activate();
        }

        /**
         * @name activate
         * @desc Actions to be performed when this controller is instantiated
         * @memberOf openDataHub.auth.controllers.AccountController
         */
        private activate() {
            var username = this.$stateParams.username;
            var that = this;
            this.AccountService.get(username).then(accountSuccessFn, accountErrorFn);

            /**
             * @name accountSuccessAccount
             * @desc Update `account` on viewmodel
             */
            function accountSuccessFn(data, status, headers, config) {
                that.account = data.data;
            }


            /**
             * @name accountErrorFn
             * @desc Redirect to index and show error Snackbar
             */
            function accountErrorFn(data, status, headers, config) {
                that.$location.url('/');
                //Snackbar.error('That user does not exist.');
            }


        }
    }
    angular.module('openDataHub').controller('AccountController', AccountController);
}
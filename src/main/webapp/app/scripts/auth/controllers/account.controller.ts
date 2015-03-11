/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class AccountController {

        private account;

        constructor(private $location, private AccountService, private $stateParams) {
            this.activate();
        }

        private activate() {
            var username = this.$stateParams.username;
            var that = this;
            this.AccountService.get(username).then((data) => {
                that.account = data.data;

            }).catch(() => {
                that.$location.url('/');
            });

        }
    }
    angular.module('openDataHub.auth').controller('AccountController', AccountController);
}

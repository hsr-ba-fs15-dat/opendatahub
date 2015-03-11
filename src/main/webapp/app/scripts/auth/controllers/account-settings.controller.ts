/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class AccountSettingsController {
        private account;

        constructor(private AuthenticationService:odh.auth.AuthenticationService, private AccountService,
                    private $state, private $stateParams) {
            this.activate();
        }

        activate() {
            var authenticatedAccount = this.AuthenticationService.getAuthenticatedAccount();
            var username = this.$stateParams.username;

            // redirect if not logged in
            if (!authenticatedAccount) {
                this.$state.go('main');
                // todo nice error Framework

            } else {
                // redirect if logged in, but not the owner of this account.
                if (authenticatedAccount.username !== username) {
                    this.$state.go('main');
                    // todo nice error Framework

                }
            }

            this.AccountService.get(username).then((data) => {
                this.account = data.data;
            }).catch(() => {
                this.$state.go('main');

            });

        }

        /**
         * Destroy this account
         */
        destroy() {
            this.AccountService.destroy(this.account.username).then(() => {
                this.AuthenticationService.unauthenticate();
                this.$state.go('main');
            }).catch(() => {
                // todo
            });
        }

        /**
         * Update this account
         */
        update() {
            var username = this.$stateParams.username;

            this.AccountService.update(username, this.account).then(() => {
                // todo
            }).catch(() => {
                // todo
            });
        }
    }
    angular.module('openDataHub').controller('AccountSettingsController', AccountSettingsController);

}

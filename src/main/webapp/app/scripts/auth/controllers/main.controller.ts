/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class MainController {
        public response:any;
        public show_login:boolean;

        constructor(
                    private AuthenticationService:odh.auth.AuthenticationService, private $scope:ng.IScope,
                    private $location:ng.ILocationService) {
            // controller init
            this.show_login = true;
            $scope.$on('djangoAuth.logged_in', function (data) {
                this.show_login = false;
            });
            $scope.$on('djangoAuth.logged_out', function (data) {
                this.show_login = true;
            });

        }

        public login() {
            this.AuthenticationService.login(prompt('Username'), prompt('password'))
                .then(function (data) {
                    this.handleSuccess(data);
                }, this.handleError);
        }

        public logout() {
            this.AuthenticationService.logout(

            ).then(this.handleSuccess, this.handleError);
        }

        public resetPasswort() {
            this.AuthenticationService.resetPassword(prompt('Email'))
                .then(this.handleSuccess, this.handleError);
        }

        public register() {
            this.AuthenticationService.register(prompt('Username'), prompt('Password'),
                prompt('Password2'), prompt('Email'))
                .then(this.handleSuccess, this.handleError);
        }

        public verify() {
            this.AuthenticationService.verify(prompt('Please enter verification code'))
                .then(this.handleSuccess, this.handleError);
        }

        public goVerify() {
            this.$location.path('/verifyEmail/' + prompt('Please enter verification code'));

        }

        public changePassword() {
            this.AuthenticationService.changePassword(prompt('Password'), prompt('Repeat Password'))
                .then(this.handleSuccess, this.handleError);
        }

        public profile() {
            this.AuthenticationService.profile()
                .then(this.handleSuccess, this.handleError);
        }

        public updateProfile() {
            this.AuthenticationService.updateProfile({
                'first_name': prompt('First Name'),
                'last_name': prompt('Last Name'),
                'email': prompt('Email')
            })
                .then(this.handleSuccess, this.handleError);
        }

        public confirmReset() {
            this.AuthenticationService.confirmReset(prompt('Code 1'), prompt('Code 2'), prompt('Password'),
                prompt('Repeat Password'))
                .then(this.handleSuccess, this.handleError);
        }

        public goConfirmReset() {
            this.$location.path('/passwordResetConfirm/' + prompt('Code 1') + '/' + prompt('Code 2'));
        }

        public handleSuccess(data) {
            this.response = data;
        }

        public handleError(data) {
            this.response = data;
        }

    }
    angular.module('openDataHub.auth').controller('MainController', MainController);
}

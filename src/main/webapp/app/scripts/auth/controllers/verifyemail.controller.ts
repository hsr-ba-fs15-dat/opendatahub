/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class VerifyEmailController {

        constructor(private $stateParams: any, private AuthenticationService:odh.auth.AuthenticationService) {
            // controller init
            AuthenticationService.verify($stateParams.emailVerificationToken).then(function (data) {
                this.success = true;
            }, function (data) {
                this.failure = false;
            });
        }
    }
    angular.module('openDataHub.auth').controller('VerifyEmailController', VerifyEmailController);
}

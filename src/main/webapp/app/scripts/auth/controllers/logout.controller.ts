/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class LogoutController {

        constructor(private AuthenticationService:odh.auth.AuthenticationService) {
            // controller init
            this.AuthenticationService.logout();
        }
    }
    angular.module('openDataHub.auth').controller('LogoutController', LogoutController);
}

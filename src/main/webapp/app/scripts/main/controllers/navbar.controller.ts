/// <reference path='../../all.d.ts' />


module odh {
    'use strict';

    class NavBarController {

        public email:string;
        public password:string;

        constructor(private $location:ng.ILocationService,
                    private AuthenticationService:odh.auth.AuthenticationService) {

        }
    }

    angular.module('openDataHub.main').controller('NavBarController', NavBarController);
}

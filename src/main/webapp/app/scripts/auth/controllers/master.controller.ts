/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class MasterController {

        public authenticated:boolean;

        constructor(private AuthenticationService:odh.auth.AuthenticationService,
                    private $scope:ng.IRootScopeService, private $location:ng.ILocationService) {
            this.AuthenticationService.authenticationStatus(true).then(function () {
                this.authenticated = true;

            });
            $scope.$on('this.AuthenticationService.logged_out', function () {
                this.authenticated = false;
            });
            $scope.$on('this.AuthenticationService.logged_in', function () {
                this.authenticated = true;
            });
            $scope.$on('$routeChangeError', function (ev, current, previous, rejection) {
                console.error('Unable to change routes.  Error: ', rejection);
                $location.path('/restricted').replace();
            });
        }

    }
    angular.module('openDataHub.auth').controller('MasterController', MasterController);
}

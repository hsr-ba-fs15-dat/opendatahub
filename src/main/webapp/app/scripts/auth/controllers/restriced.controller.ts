/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class RestrictedController {

        public myTemplateAccessedAttribute:string;

        constructor(private $scope:ng.IScope, private $location:ng.ILocationService) {
            // controller init
            $scope.$on('auth.logged_in', function () {
                $location.path('/');
            });
        }


    }
    angular.module('openDataHub.auth').controller('RestrictedController', RestrictedController);
}

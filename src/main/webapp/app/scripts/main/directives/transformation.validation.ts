/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export class OdhValidateTransformation implements ng.IDirective {
        static $inject = ['$q', 'TransformationService'];

        constructor(private $q, private TransformationService:main.TransformationService) {
        }

        require = 'ngModel';
        scope = {
            errorMessage: '=odhValidateTransformation'
        };
        link = (scope, elm, attrs, ngModel) => {
            ngModel.$asyncValidators.transformation = (modelValue, viewValue) => {

                var def = this.$q.defer();
                this.TransformationService.parse(viewValue).then((res) => {
                    scope.errorMessage = undefined;
                    def.resolve();
                }).catch((res) => {
                    scope.errorMessage = res.data;
                    def.reject();
                });

                return def.promise;
            };
        };

    }

    angular.module('openDataHub.main').directive('odhValidateTransformation',
        ($q, TransformationService) => {
            return new OdhValidateTransformation($q, TransformationService);
        }
    )
    ;
}

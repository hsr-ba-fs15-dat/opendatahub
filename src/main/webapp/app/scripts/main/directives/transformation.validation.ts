/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export class OdhValidateTransformation implements ng.IDirective {
        static $inject = ['$q', 'TransformationService'];

        constructor(private $q, private TransformationService:main.TransformationService) {
        }

        require = 'ngModel';
        link = (scope, elm, attrs, ctrl) => {
            ctrl.$asyncValidators.odhValidateTransformation = function (modelValue, viewValue) {

                var def = this.$q.defer();
                console.log(modelValue);

                this.TransformationService.parse(modelValue).then((res) => {
                    console.log(res);
                    def.resolve();
                }).catch((res) => {
                    console.log(res);
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

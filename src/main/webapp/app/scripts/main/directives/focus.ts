/// <reference path='../../all.d.ts' />

module odh {
    'use strict';

    function odhFocus($timeout:ng.ITimeoutService):ng.IDirective {
        return {
            restrict: 'A',
            require: '^form',
            link: (scope:ng.IScope, element:JQuery, attrs:any, form:ng.IFormController) => {
                var expr:string = attrs.odhFocus;
                scope.$watch(expr, function (newVal:any, oldVal:any) {
                    if (newVal) {
                        $timeout(function () {
                            element[0].focus();
                            // revert user interaction flag
                            form.$setUntouched();
                        });
                    }
                });
            }
        };
    }
    angular.module('openDataHub').directive('odhFocus', odhFocus);

}

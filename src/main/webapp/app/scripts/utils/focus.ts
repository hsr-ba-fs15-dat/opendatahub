/// <reference path='../all.d.ts' />

module odh.utils {
    'use strict';
    /**
     * sets focus to an element
     * @param $timeout
     * @returns {{restrict: string, require: string,
     * link: (function(ng.IScope, JQuery, any, ng.IFormController): undefined)}}
     */
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

/// <reference path='../all.d.ts' />
'use strict';

/**
 * @ngdoc directive
 * @name opendatahubApp.directive:odhFocus
 * @description
 * # focus input field on condition
 */
function odhFocus($timeout):ng.IDirective {
    return {
        restrict: 'A',
        require: '^form',
        link: (scope:ng.IScope, element:JQuery, attrs:any, form) => {
            var expr = attrs.odhFocus;
            scope.$watch(expr, function (newVal, oldVal) {
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

app.directive('odhFocus', odhFocus);

/// <reference path='../all.d.ts' />


module odh.utils {
    'use strict';
    /**
     * provides the loading spinner
     * @returns {{restrict: string, transclude: boolean, template: string, scope: {showWhile: string}}}
     */
    function odhSpinner():ng.IDirective {
        return {
            restrict: 'E',
            transclude: true,
            template: '<div ng-show="showWhile"><svg class="spinner" width="65px" height="65px" viewBox="0 0 66 66"' +
            'xmlns="http://www.w3.org/2000/svg"><circle class="path" fill="none" stroke-width="6" ' +
            'stroke-linecap="round" cx="33" cy="33" r="30"></circle></svg></div>' +
            '<div ng-transclude ng-hide="showWhile"></div>',
            scope: {
                showWhile: '='
            }
            // link: (scope:ng.IScope, element:JQuery, attrs:any) => {
            // }
        };
    }

    angular.module('openDataHub').directive('odhSpinner', odhSpinner);
}

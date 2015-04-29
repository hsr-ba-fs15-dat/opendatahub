/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    function odhChooseTransformation():ng.IDirective {
        return {

            restrict: 'AE',
            templateUrl: 'views/transformation.table_choose.html',
            scope: {
                tableParams: '=',
                isAuthenticated: '&',
                addRemoveTable: '&',
                checkTableSelected: '&',
                getFileGroup: '&'
            }
        };
    }

    angular.module('openDataHub.main').directive('odhChooseTransformation', odhChooseTransformation);
}

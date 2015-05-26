/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    function odhTablePagination($compile:ng.ICompileService):ng.IDirective {
        return {
            restrict: 'A',
            scope: {
                'params': '=odhTablePagination',
                'templateUrl': '='
            },
            replace: false,
            link: function (scope:any, element, attrs) {
                console.log(scope);
                var watchRegister = scope.$watch('params.settings().$scope', function ($scope, oldValue) {
                    console.log(scope);
                    if (scope.params) {
                        scope.pages = scope.params.generatePagesArray(
                            scope.params.page(), scope.params.total(), scope.params.count()
                        );
                    }
                    if ($scope !== oldValue && $scope) {
                        $scope.$on('ngTableAfterReloadData', function () {

                            scope.pages = scope.params.generatePagesArray(
                                scope.params.page(), scope.params.total(), scope.params.count()
                            );
                        });
                        watchRegister();
                    }
                });

                scope.$watch('templateUrl', function (templateUrl) {
                    if (angular.isUndefined(templateUrl)) {
                        return;
                    }
                    var template = angular.element(document.createElement('div'));
                    template.attr({
                        'ng-include': 'templateUrl'
                    });
                    element.append(template);
                    $compile(template)(scope);
                });
            }
        };
    }

    angular.module('openDataHub').directive('odhTablePagination', odhTablePagination);
}

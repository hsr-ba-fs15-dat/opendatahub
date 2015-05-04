/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export class OdhPreview implements ng.IDirective {
        static $inject = ['FileGroupService:main.FileGroupService', 'ngTableParams:any'];
        public modal:boolean = false;

        constructor(private FileGroupService:main.FileGroupService, private ngTableParams:any) {
        }


        restrict = 'AE';
        templateUrl = 'views/directives/preview.html';

        scope = {
            table: '='
        };
        link = (scope, element, attrs) => {
            angular.forEach(scope.table.columns, (col) => {
                scope.cols = scope.cols || [];
                scope.cols.push({
                    name: col,
                    alias: col,
                    title: col,
                    show: true,
                    field: col
                });
            });
            scope.ngTableParams = new this.ngTableParams({
                    page: 1,            // show first page
                    count: 3           // count per page
                },
                {
                    counts: [3, 10, 25, 100],
                    total: 0, // length of data
                    getData: ($defer, params) => {
                        console.log(scope.table, 'table');
                        if (typeof scope.table === 'object') {
                            this.FileGroupService.getPreview(scope.table.parent, params.url(), scope.table.name)
                                .then(result => {

                                    params.total(result.data[0].count);
                                    $defer.resolve(result.data[0].data);

                                }).catch(err => console.error(err));
                        }
                    }
                });
        }

    }

    angular.module('openDataHub.main').directive('odhPreview',
        (FileGroupService:main.FileGroupService,
         ngTableParams:any) => {
            return new OdhPreview(FileGroupService, ngTableParams);
        }
    )
    ;
}

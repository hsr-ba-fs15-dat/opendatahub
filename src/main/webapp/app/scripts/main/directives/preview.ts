/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export class OdhPreview implements ng.IDirective {
        static $inject = ['FileGroupService:main.FileGroupService', 'ngTableParams:any'];
        public modal:boolean = false;

        constructor(private FileGroupService:main.FileGroupService, private ngTableParams:any,
                    private PackageService:main.PackageService,
                    private $q:ng.IQService) {
        }


        restrict = 'AE';
        templateUrl = 'views/directives/preview.html';

        scope = {
            pkg: '=',
            query: '='
        };
        link = (scope:ng.IScope, element, attrs) => {
            this.ngTable(scope);
            scope.$watch('pkg', (oldVal, newVal) => {
                console.log(444444444444, oldVal, newVal, oldVal === newVal);
                if (oldVal !== newVal) {
                    this.ngTable(scope);
                }


            })


        };

        public ngTable(scope) {
            scope.pkgNew = this.$q.when(scope.pkg);
            scope.cols = [];

            scope.pkgNew.then(pack => {
                console.log('===>', pack);
                scope.ngTableParams = new this.ngTableParams({
                        page: 1,            // show first page
                        name: pack.unique_name || '',
                        query: scope.query || '',
                        count: 3           // count per page
                    },
                    {
                        counts: [3, 10, 25, 100],
                        total: 0, // length of data

                        getData: ($defer, params) => {
                            console.log('get_data');
                            if (typeof pack === 'object') {
                                this.PackageService.getPreview(pack, params.url()).then(result => {
                                    console.log('getPreview')
                                    var data = result.data;
                                    if (result.data.length === 1) {
                                        data = result.data[0];
                                    }
                                    if (result.data.length > 1) {
                                        throw "Only one preview excepted!! Got " + result.data.length
                                    }
                                    angular.forEach(data.columns, (col) => {
                                        scope.cols.push({
                                            name: col,
                                            alias: col,
                                            title: col,
                                            show: true,
                                            field: col
                                        });
                                    });
                                    params.total(data.count);
                                    $defer.resolve(data.data);
                                });
                            }
                        }
                    });
            });
        }
    }

    angular.module('openDataHub.main').directive('odhPreview',
        (FileGroupService:main.FileGroupService,
         ngTableParams:any,
         PackageService:main.PackageService,
         $q:ng.IQService) => {
            return new OdhPreview(FileGroupService, ngTableParams, PackageService, $q);
        }
    )
    ;
}

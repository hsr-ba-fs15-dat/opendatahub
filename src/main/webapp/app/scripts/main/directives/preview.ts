/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export class OdhPreview implements ng.IDirective {
        static $inject = ['FileGroupService:main.FileGroupService', 'ngTableParams:any'];
        public modal:boolean = false;

        constructor(private TransformationService:main.TransformationService, private ngTableParams:any,
                    private PackageService:main.PackageService,
                    private $q:ng.IQService, private ToastService:odh.utils.ToastService,
                    private FormatService:main.FormatService) {
        }
        success = false;
        availableFormats = [];
        restrict = 'AE';
        templateUrl = 'views/directives/preview.html';

        scope = {
            pkg: '=',
            query: '=',
            download: '&'
        };
        link = (scope:ng.IScope, element, attrs) => {
            this.ngTable(scope);
            scope.$watch('pkg', (oldVal, newVal) => {
                if (oldVal !== newVal) {
                    this.ngTable(scope);
                }
            });

            this.FormatService.getAvailableFormats().then(data => {
                var results = this.FormatService.sortByLabel(data.data);
                results.push({name: null, label: 'Original', description: 'Unveränderte Daten', example: null});
                scope.availableFormats = results;
            });
        };

        public ngTable(scope) {
            scope.pkgNew = this.$q.when(scope.pkg);
            scope.cols = [];

            scope.pkgNew.then(pack => {
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
                            scope.success = false;
                            if (typeof pack === 'object') {
                                if (!(scope.query && (pack.route !== 'transformation'))) {
                                    this.PackageService.getPreview(pack, params.url()).then(result => {
                                        var data = result.data;
                                        console.log(data, ',===')
                                        if (result.data.length === 1) {
                                            data = result.data[0];
                                        }
                                        if (result.data.length > 1) {
                                            throw "Only one preview excepted!! Got " + result.data.length
                                        }
                                        scope.cols = [];
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
                                        scope.success = true;
                                    }).catch(error => {
                                        this.ToastService.failure(error);
                                    });
                                } else {
                                    this.TransformationService.preview(scope.query, params.url()).then((result) => {
                                        var data = result;
                                        scope.cols = [];
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
                                        scope.success = true;
                                    }).catch(error => {
                                        this.ToastService.failure(error);
                                    });
                                }
                            }
                        }
                    });
            });
        }
    }

    angular.module('openDataHub.main').directive('odhPreview',
        (TransformationService:main.TransformationService,
         ngTableParams:any,
         PackageService:main.PackageService,
         $q:ng.IQService,
         ToastService:odh.utils.ToastService,
         FormatService:main.FormatService) => {
            return new OdhPreview(TransformationService, ngTableParams, PackageService, $q, ToastService, FormatService);
        }
    )
    ;
}

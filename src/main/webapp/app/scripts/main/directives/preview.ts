/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export class OdhPreview implements ng.IDirective {
        static $inject = ['FileGroupService:main.FileGroupService', 'ngTableParams:any'];
        public modal:boolean = false;

        constructor(private TransformationService:main.TransformationService, private NgTableParams:any,
                    private PackageService:main.PackageService,
                    private $q:ng.IQService, private ToastService:odh.utils.ToastService,
                    private FormatService:main.FormatService) {
        }

        alerts = [];
        success = false;
        showDownload = false;
        availableFormats = [];
        restrict = 'AE';
        templateUrl = 'views/directives/preview.html';

        scope = {
            pkg: '=',
            query: '=',
            download: '&'
        };
        link = (scope, element, attrs) => {
            if (scope.download) {
                scope.showDownload = true;
            }
            this.ngTable(scope);
            if (scope.pkg) {
                scope.$watch('pkg', (oldVal, newVal) => {
                    if (oldVal !== newVal) {
                        this.ngTable(scope);
                    }
                });

            }
            if (scope.query) {
                scope.$watch('query', (oldVal, newVal) => {
                    if (oldVal !== newVal) {
                        this.ngTable(scope);
                    }
                });
            }


            this.FormatService.getAvailableFormats().then(data => {
                var results = this.FormatService.sortByLabel(data.data);
                results.push({name: null, label: 'Original', description: 'Unveränderte Daten', example: null});
                scope.availableFormats = results;
            });

            scope.closeAlert = (index) => {
                scope.alerts.splice(index, 1);
            };
        };


        public ngTable(scope) {
            scope.pkgNew = this.$q.when(scope.pkg);
            scope.cols = [];
            scope.alerts = [];
            scope.pkgNew.then(pack => {
                var name = '';
                if (pack) {
                    name = pack.unique_name;
                }
                scope.ngTableParams = new this.NgTableParams({
                        page: 1,            // show first page
                        name: name || '',
                        query: scope.query || '',
                        count: 3           // count per page
                    },
                    {
                        counts: [3, 10, 25, 100],
                        total: 0, // length of data

                        getData: ($defer, params) => {
                            scope.success = false;
                            if (typeof pack === 'object' && !(scope.query && (pack.route !== 'transformation'))) {
                                this.PackageService.getPreview(pack, params.url()).then(data => {
                                    console.log(data);
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
                                    console.log(error, 'error');
                                    this.ToastService.failure('Fehler beim erstellen der Vorschau');
                                });
                            } else if (scope.query.length > 5) {
                                this.TransformationService.preview(scope.query, params.url()).then((result:any) => {
                                    scope.cols = [];
                                    angular.forEach(result.columns, (col) => {
                                        scope.cols.push({
                                            name: col,
                                            alias: col,
                                            title: col,
                                            show: true,
                                            field: col
                                        });
                                    });
                                    params.total(result.count);
                                    $defer.resolve(result.data);
                                    scope.success = true;
                                }).catch(error => {
                                    console.log('error');
                                    scope.alerts.push({
                                        title: error.data.type,
                                        msg: error.data.error

                                    });
                                    this.ToastService.failure('Es ist ein Fehler aufgetreten');
                                });
                            }
                        }
                    });
            }).catch(error => {
                    this.ToastService.failure('Die Vorschau konnte nicht erstellt werden.');
                    console.error(error);
                    if (error.data.type === 'execution') {
                        scope.alerts.push({
                            title: 'Fehler ( ' + error.data.type + ')',
                            msg: error.data.error,
                            type: 'danger'
                        });
                    }
                    if (error.data.type === 'parse') {
                        scope.alerts.push({
                            title: 'Fehler (' + error.data.type + ')',
                            msg: error.data.error + '(Line: ' + error.data.lineno +
                            ', Col: ' + error.data.col +
                            ') at ' + error.data.line,
                            type: 'danger'
                        });
                    }

                }
            );
        }
    }

    angular.module('openDataHub.main').directive('odhPreview',
        (TransformationService:main.TransformationService,
         ngTableParams:any,
         PackageService:main.PackageService,
         $q:ng.IQService,
         ToastService:odh.utils.ToastService,
         FormatService:main.FormatService) => {
            return new OdhPreview(TransformationService, ngTableParams, PackageService, $q, ToastService,
                FormatService);
        }
    )
    ;
}

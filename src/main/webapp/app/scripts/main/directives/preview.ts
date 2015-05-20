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

        loaded = false;
        alerts = [];
        restrict = 'AE';
        templateUrl = 'views/directives/preview.html';

        scope = {
            pkg: '=',
            query: '=',
            success: '=',
            alerts: '=',
            preview: '='
        };

        link = (scope, element, attrs) => {
            scope.loaded = false;
            scope.$watch('preview', (oldVal, newVal) => {
                if (oldVal !== newVal && newVal !== '') {
                    this.tableDirect(scope, attrs);
                }
            });
            if (scope.pkg) {
                this.ngTable(scope, attrs);
                scope.$watch('pkg', (oldVal, newVal) => {
                    if (oldVal !== newVal) {
                        this.ngTable(scope, attrs);
                    }
                });

            }
            if (scope.query) {
                this.ngTable(scope, attrs);
                scope.$watch('query', (oldVal, newVal) => {
                    if (oldVal !== newVal) {
                        this.ngTable(scope, attrs);
                    }
                });
            }

            scope.closeAlert = (index) => {
                scope.alerts.splice(index, 1);
            };
        };

        public tableDirect(scope, attr) {
            if (!scope.preview) {
                return false;
            }
            if (scope.preview.error) {
                scope.preview.alerts = [];
                this.displayError(scope.preview.error, scope.preview);
            }
            scope.adHocCols = [];
            scope.adHocPreview = scope.preview;
            angular.forEach(scope.preview.columns, (col) => {
                scope.adHocCols.push({
                    name: col,
                    alias: col,
                    title: col,
                    show: true,
                    field: col
                });
            });
            scope.success = true;
            scope.loaded = true;
        }

        public ngTable(scope, attr) {
            scope.adHocPreview = undefined;
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
                        // name: name || '',
                        query: scope.query || '',
                        count: 3           // count per page
                    },
                    {
                        counts: [3, 10, 25, 100],
                        total: 0, // length of data

                        getData: ($defer, params) => {
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
                                    this.displayError(error, scope);
                                    this.ToastService.failure('Fehler beim erstellen der Vorschau');
                                }).finally(() => {
                                    scope.loaded = true;
                                });
                            } else if (!!scope.query && scope.query.length > 5) {
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
                                    this.displayError(error, scope);
                                    this.ToastService.failure('Es ist ein Fehler aufgetreten');
                                }).finally(() => {
                                    scope.loaded = true;
                                });
                            }

                        }
                    });
            }).catch(error => {
                    this.ToastService.failure('Die Vorschau konnte nicht erstellt werden.');
                    this.displayError(error, scope);

                }
            );
        }

        public displayError(error, scope = null) {
            if (error.data.type === 'execution') {
                scope.alerts.push({
                    title: 'Fehler ( ' + error.data.type + ')',
                    msg: error.data.error || 'Es ist ein Fehler Aufgetreten',
                    type: 'warning'
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

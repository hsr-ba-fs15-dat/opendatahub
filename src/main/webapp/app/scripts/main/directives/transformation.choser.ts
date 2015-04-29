/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export class odhChooseTransformation implements ng.IDirective {
        static $inject = ['private DocumentService:main.DocumentService', 'ngTableParams:any',
            'FileGroupService:main.FileGroupService', '$auth:any', 'ToastService:odh.utils.ToastService'];

        constructor(private DocumentService:main.DocumentService, private ngTableParams:any, private $auth:any,
                    private FileGroupService:main.FileGroupService, private ToastService:odh.utils.ToastService) {
        }


        restrict = 'AE';
        templateUrl = 'views/transformation.table_choose.html';
        scope = {
            addRemoveTable: '&',
            checkTableSelected: '&'
        };
        link = (scope) => {
            scope.tableParams = new this.ngTableParams({
                page: 1,            // show first page
                count: 10           // count per page
            }, {
                counts: [10, 25, 50, 100],
                total: 0, // length of data
                getData: ($defer, params) => {
                    this.DocumentService.getList(params.url()).then(result => {
                        params.total(result.count);
                        $defer.resolve(result.results);
                    });
                }
            });
            scope.isAuthenticated = () => {
                return this.$auth.isAuthenticated();
            };

            scope.getFileGroup = (document, count = 3) => {
                this.FileGroupService.getAll(document.id, true, count).then(filegroups => {
                    if (!document.$showRows) {
                        angular.forEach(filegroups, (fg) => {
                            angular.forEach(fg.preview, (preview) => {
                                preview.uniqueId = preview.unique_name;
                                preview.cols = [];
                                preview.parent = fg.id;
                                preview.private = document.private;
                                angular.forEach(preview.columns, (col) => {
                                    preview.cols.push({name: col, alias: col, type: preview.types[col]});
                                });
                            });
                        });
                        document.fileGroup = filegroups;
                    } else {
                        document.fileGroup = [];
                    }
                    document.$showRows = !document.$showRows;
                }).catch(error => this.ToastService.failure('Es ist ein Fehler aufgetreten.'));
            }


        };


    }

    angular.module('openDataHub.main').directive('odhChooseTransformation',
        (DocumentService:main.DocumentService, ngTableParams:any, $auth:any, FileGroupService:main.FileGroupService,
         ToastService:odh.utils.ToastService) => {
            return new odhChooseTransformation(DocumentService, ngTableParams, $auth, FileGroupService, ToastService);
        });
}

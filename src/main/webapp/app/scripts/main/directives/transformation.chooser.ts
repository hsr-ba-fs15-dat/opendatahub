/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export class OdhChooseTransformation implements ng.IDirective {
        static $inject = ['private DocumentService:main.DocumentService', 'ngTableParams:any',
            'FileGroupService:main.FileGroupService', '$auth:any', 'ToastService:odh.utils.ToastService'];
        public modal:boolean = false;

        constructor(private TransformationService:main.TransformationService, private ngTableParams:any,
                    private $auth:any, private FileGroupService:main.FileGroupService,
                    private ToastService:odh.utils.ToastService, private PackageService:main.PackageService) {
        }


        restrict = 'AE';
        templateUrl = (modal) => {
            modal = modal.context.attributes.modal;
            if (!modal) {
                return 'views/directives/transformation.table_choose.html';
            } else {
                return 'views/directives/transformation.table_choose.modal.html';
            }
        };
        scope = {
            addRemoveTable: '&',
            checkTableSelected: '&',
            modal: '=',
            modalVisible: '=',
            modalOpener: '='
        };
        link = (scope, element, attrs) => {
            var modal = element.find('#modal');
            scope.toggleModal = () => {
                scope.modalVisible = !scope.modalVisible;
                if (scope.modalVisible) {
                    modal.modal('show');
                } else {
                    modal.modal('hide');
                }
            };


            scope.tableParams = new this.ngTableParams({
                page: 1,            // show first page
                count: 10           // count per page
            }, {
                counts: [10, 25, 50, 100],
                total: 0, // length of data
                getData: ($defer, params) => {
                    this.PackageService.getList(params.url()).then(result => {
                        params.total(result.count);
                        $defer.resolve(result.results);
                    });
                }
            });
            scope.isAuthenticated = () => {
                return this.$auth.isAuthenticated();
            };

            scope.getFileGroup = (pkg, count = 3) => {
                if (pkg.type === 'transformation') {
                    this.TransformationService.preview(pkg).then(data => {
                        if (!pkg.$showRows) {
                            var filegroups = [{
                                preview: [
                                    data[0]

                                ]
                            }];
                            var preview = filegroups[0].preview[0];
                            preview.uniqueId = preview.unique_name;
                            preview.cols = [];
                            preview.private = pkg.private;
                            angular.forEach(preview.columns, (col) => {
                                preview.cols.push({
                                    name: col,
                                    alias: col,
                                    type: preview.types[col],
                                    title: col,
                                    parent: 0,
                                    show: true,
                                    field: col
                                });
                            });
                            pkg.fileGroup = filegroups;
                        } else {
                            pkg.fileGroup = [];
                        }
                        pkg.$showRows = !pkg.$showRows;
                    })
                        .catch(error => this.ToastService.failure('Es ist ein Fehler aufgetreten.'));

                }
                if (pkg.type === 'document') {
                    this.FileGroupService.getAll(pkg.id, true, count).then(filegroups => {
                        if (!pkg.$showRows) {
                            angular.forEach(filegroups, (fg) => {
                                angular.forEach(fg.preview, (preview) => {
                                    preview.uniqueId = preview.unique_name;
                                    preview.cols = [];
                                    preview.parent = fg.id;
                                    preview.private = pkg.private;
                                    angular.forEach(preview.columns, (col) => {
                                        preview.cols.push({
                                            name: col,
                                            alias: col,
                                            type: preview.types[col],
                                            title: col,
                                            show: true,
                                            field: col
                                        });
                                    });
                                });
                            });
                            pkg.fileGroup = filegroups;
                        } else {
                            pkg.fileGroup = [];
                        }
                        pkg.$showRows = !pkg.$showRows;
                    }).catch(error => this.ToastService.failure('Es ist ein Fehler aufgetreten.'));
                }
            };
        };


    }

    angular.module('openDataHub.main').directive('odhChooseTransformation',
        (TransformationService:main.TransformationService,
         ngTableParams:any,
         $auth:any,
         FileGroupService:main.FileGroupService,
         ToastService:odh.utils.ToastService, PackageService:main.PackageService) => {
            return new OdhChooseTransformation(
                TransformationService, ngTableParams, $auth, FileGroupService, ToastService, PackageService);
        }
    )
    ;
}

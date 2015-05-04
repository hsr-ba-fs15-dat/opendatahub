/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export class OdhChooseTransformation implements ng.IDirective {
        static $inject = ['private DocumentService:main.DocumentService', 'ngTableParams:any',
            'FileGroupService:main.FileGroupService', '$auth:any', 'ToastService:odh.utils.ToastService'];
        public modal:boolean = false;

        constructor(private DocumentService:main.DocumentService, private ngTableParams:any, private $auth:any,
                    private FileGroupService:main.FileGroupService, private ToastService:odh.utils.ToastService) {
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
                        document.fileGroup = filegroups;
                    } else {
                        document.fileGroup = [];
                    }
                    document.$showRows = !document.$showRows;
                }).catch(error => this.ToastService.failure('Es ist ein Fehler aufgetreten.'));
            };
        };


    }

    angular.module('openDataHub.main').directive('odhChooseTransformation',
        (DocumentService:main.DocumentService,
         ngTableParams:any,
         $auth:any,
         FileGroupService:main.FileGroupService,
         ToastService:odh.utils.ToastService, $modal) => {
            return new OdhChooseTransformation(
                DocumentService, ngTableParams, $auth, FileGroupService, ToastService);
        }
    )
    ;
}

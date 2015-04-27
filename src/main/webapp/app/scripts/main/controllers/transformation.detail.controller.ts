/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    class TransformationDetailController implements main.ITransformation {

        public name;
        public description;
        public transformationId;
        public transformation;
        public file_groups;
        public 'private';
        public columns;
        public rows;
        public alerts;
        public fileGroupTable;

        constructor(private $log:ng.ILogService, private $stateParams:any,
                    private TransformationService:main.TransformationService, private $http:ng.IHttpService,
                    private $state:ng.ui.IStateService, private $scope:any,
                    private ToastService:odh.utils.ToastService, private $window:ng.IWindowService, private $upload,
                    private UrlService:odh.utils.UrlService, private FileGroupService:main.FileGroupService,
                    private DocumentService:main.DocumentService,
                    private ngTableParams, public $filter:ng.IFilterService,
                    private $auth:any) {
            // controller init
            this.transformationId = $stateParams.id;
            this.TransformationService.get(this.transformationId).then(data => {
                this.name = data.name;
                this.description = data.description;
                this.transformation = data.transformation;
                this.private = data.private;

            });
            this.fileGroupTable = new ngTableParams({
                    page: 1,
                    count: 10
                }, {
                    counts: [10, 25, 50, 100],
                    total: 0,
                    getData: ($defer, params) => {
                        this.TransformationService.get(this.transformationId).then(result => {
                            console.log(result)
                            params.total(result.file_groups.length);
                            $defer.resolve(result.file_groups);
                        });

                    }
                }
            )

        }


        public aceLoaded(editor) {
            editor.$blockScrolling = 'Infinity';
            editor.setOptions({
                maxLines: Infinity
            });
        }

        public preview() {
            this.TransformationService.preview(this.transformation).then((data:any) => {
                this.columns = data.data.columns;
                this.rows = data.data.data;
            }).catch((data:any) => {
                data = data.data.split('\n');
                this.ToastService.failure(
                    'Es ist ein Fehler aufgetreten! (Fehlermeldung in der Konsole ersichtlich.) ' + data[1]);
                this.alerts.push({msg: data.slice(0, 3).join('\n'), type: 'danger', title: 'Fehler:'});
            });
        }


    }
    angular.module('openDataHub.main').controller('TransformationDetailController', TransformationDetailController);
}

/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';
    enum transType {Template, Final}
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
        public usedTables:{};
        public previewError;
        public selected;
        public transformationType:transType = transType.Template;

        public allowDelete:boolean;

        constructor(private $stateParams:any,
                    private TransformationService:main.TransformationService,
                    private $state:ng.ui.IStateService,
                    private ToastService:odh.utils.ToastService,
                    private ngTableParams,
                    private $auth:any,
                    private ngTableParams, public $filter:ng.IFilterService,
                    private $modal:ng.ui.bootstrap.IModalService) {
            // controller init
            this.transformationId = $stateParams.id;
            this.TransformationService.get(this.transformationId).then(data => {
                this.name = data.name;
                this.description = data.description;
                this.transformation = data.transformation;
                this.private = data.private;

                this.allowDelete = data.owner.id === $auth.getPayload().user_id;

                this.preview();
                this.selected = {};

            });
            this.fileGroupTable = new ngTableParams({
                    page: 1,
                    count: 10
                }, {
                    counts: [],
                    total: 0,
                    getData: ($defer, params) => {
                        this.TransformationService.get(this.transformationId).then(result => {
                            this.selected.vals = result.file_groups;
                            console.log(this.selected);
                            params.total(result.file_groups.length);
                            $defer.resolve(result.file_groups);
                        });

                    }
                }
            );

        }


        public aceLoaded(editor) {
            editor.$blockScrolling = 'Infinity';
            editor.setOptions({
                maxLines: Infinity
            });
        }

        public preview() {
            this.TransformationService.parse(this.transformation).then((data:any) => {
                this.usedTables = data.data.tables;
            });
            this.TransformationService.preview(this.transformation).then((data:any) => {
                this.columns = data.data.columns;
                this.rows = data.data.data;
            }).catch((data:any) => {
                this.columns = null;
                this.rows = null;
                this.previewError = 'Diese Transformation enthält (noch) keine gültigen Daten';
                this.ToastService.failure('Diese Transformation enthält keine gültigen Daten');
                this.alerts.push({msg: data.error, type: 'danger', title: 'Fehler:'});
            });
        }

        public remove() {
            var instance = this.$modal.open({
                templateUrl: 'views/transformation.deleteconfirmation.html',
                controller: 'DeleteTransformationController as vm'
            });
            instance.result.then(() => {
                    this.TransformationService.remove({id: this.transformationId}).then(() =>
                            this.$state.go('transformation.list')
                    ).catch((err) =>
                            this.ToastService.failure('Beim Löschen der Transformation ist ein Fehler aufgetreten.')
                    );
                }
            );
        }
    }

    class DeleteTransformationController {
        constructor(private $modalInstance: ng.ui.bootstrap.IModalServiceInstance) {
        }

        public ok() {
            this.$modalInstance.close();
        }

        public cancel() {
            this.$modalInstance.dismiss('cancel');
        }
    }

    angular.module('openDataHub.main')
        .controller('TransformationDetailController', TransformationDetailController)
        .controller('DeleteTransformationController', DeleteTransformationController);
}

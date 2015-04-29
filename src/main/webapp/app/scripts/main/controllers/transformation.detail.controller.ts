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
        public alerts:any;
        public fileGroupTables:ITable[] = [];
        public usedTables:{};
        public previewError;
        public selected;
        public transformationType:transType = transType.Template;
        public availableFormats;

        public previewLoading:boolean;

        public showExpertPanel = false;

        public allowDelete:boolean;
        public transformationPrefix:string;
        public packagePrefix:string;

        constructor(private $stateParams:any,
                    private TransformationService:main.TransformationService,
                    private FormatService:odh.main.FormatService,
                    private $state:ng.ui.IStateService,
                    private ToastService:odh.utils.ToastService,
                    private $auth:any,
                    private $modal:ng.ui.bootstrap.IModalService,
                    private AppConfig:odh.IAppConfig,
                    private $window:ng.IWindowService) {

            // controller init
            AppConfig.then(config => {
                this.transformationPrefix = config.TRANSFORMATION_PREFIX;
                this.packagePrefix = config.PACKAGE_PREFIX;
            });
            this.fileGroupTables = [];
            this.transformationId = $stateParams.id;
            this.TransformationService.get(this.transformationId).then(data => {
                this.name = data.name;
                this.description = data.description;
                this.transformation = data.transformation;
                this.private = data.private;

                this.allowDelete = $auth.isAuthenticated() && data.owner.id === $auth.getPayload().user_id;

                this.preview();
                this.selected = {};
            });


        }

        /**
         * Checks if this Table could belongs to our system.
         */

        public checkIfOurTable(table:main.ITable) {
            var rxQry = '^({0}|{1})\\d+_.*$'.format(this.packagePrefix, this.transformationPrefix);
            var regEx = new RegExp(rxQry);
            return regEx.test(table.name);
        }

        public checkIfTableInDB(table:main.ITable) {
            if (this.checkIfOurTable(table)) {
                // todo: check if table name exists in database


            }
            return this.checkIfOurTable(table);
        }

        public aceLoaded(editor) {
            editor.$blockScrolling = 'Infinity';
            editor.setOptions({
                maxLines: Infinity
            });
        }

        public preview() {
            this.previewLoading = true;
            this.TransformationService.parse(this.transformation).then((data:any) => {
                this.usedTables = data.data.tables;
            });
            this.TransformationService.preview(this.transformation).then((data:any) => {
                this.previewLoading = false;
                this.columns = data.data.columns;
                this.rows = data.data.data;
            }).catch((data:any) => {
                this.previewLoading = false;
                this.columns = null;
                this.rows = null;
                this.previewError = 'Diese Transformation enthält (noch) keine gültigen Daten';
                this.ToastService.failure('Diese Transformation enthält keine gültigen Daten');
            });
        }

        public downloadAs(formatName) {
            this.$window.location.href = '/api/v1/transformation/' + this.transformationId + '/?fmt=' + formatName;
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
        constructor(private $modalInstance:ng.ui.bootstrap.IModalServiceInstance) {
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

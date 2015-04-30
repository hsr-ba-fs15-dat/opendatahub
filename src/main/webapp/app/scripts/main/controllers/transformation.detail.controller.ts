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
        public loadedTables:{} = {};
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
        public isOwn:boolean;

        constructor(private $stateParams:any,
                    private TransformationService:main.TransformationService,
                    private FormatService:odh.main.FormatService,
                    private $state:ng.ui.IStateService,
                    private ToastService:odh.utils.ToastService,
                    private $auth:any,
                    private $modal:ng.ui.bootstrap.IModalService,
                    private AppConfig:odh.IAppConfig,
                    private FileGroupService:main.FileGroupService,
                    private UrlService:odh.utils.UrlService,
                    private $window:ng.IWindowService) {
            // controller init
            AppConfig.then(config => {
                this.transformationPrefix = config.TRANSFORMATION_PREFIX;
                this.packagePrefix = config.PACKAGE_PREFIX;
            });
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
            FormatService.getAvailableFormats().then(data => {
                this.availableFormats = data.data;
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

        public loadIfPackageUsed(table:main.ITable) {
            if (this.checkIfOurTable(table)) {
                this.FileGroupService.getPreviewByUniqueName(table.name).then(result => {
                    if (result[0]) {
                        this.loadedTables[result[0].unique_name] = result[0];
                        this.selected[table.name] = result[0];
                    }
                });
            }
        }

        public addRemoveTable(table:main.ITable) {
            var index = this.loadedTables[table.unique_name];
            console.log(table, index);
            if (index) {
                delete this.loadedTables[table.unique_name];
            } else {
                this.loadedTables[table.unique_name] = table;
            }
            console.log(this.loadedTables);
        }

        public checkTableSelected(table) {
            /**
             * Checks if the Table is selected.
             * @returns boolean
             */
            return typeof this.loadedTables[table.unique_name] !== 'undefined';
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
                angular.forEach(data.data.tables, table => {
                    table.isOwn = this.loadIfPackageUsed(table);
                });
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

        public duplicateTransformation() {
            this.$state.go('transformation-create', {
                name: this.name,
                description: this.description,
                odhql: this.transformation
            });
        }

        public downloadAs(formatName) {
            this.$window.location.href = this.UrlService.get('transformation/{{id}}/data',
                {id: this.transformationId}) + '?fmt=' + formatName;
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

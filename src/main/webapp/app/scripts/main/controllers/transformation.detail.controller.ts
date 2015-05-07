/// <reference path='../../all.d.ts' />

module odh.main {
    'use strict';

    enum transType {Template, Final}
    class TransformationDetailController implements main.ITransformation {
        public pkg;
        public name;
        public description;
        public transformationId;
        public transformation;
        public file_groups;
        public 'private';
        public alerts:any;
        public loadedTables:{} = {};
        public usedTables:{};
        public selected;
        public transformationType:transType = transType.Template;
        public availableFormats;
        public showExpertPanel = false;

        public allowDelete:boolean;
        public transformationPrefix:string;
        public packagePrefix:string;
        public isOwn:boolean;
        public transformationObject:any;

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
                    private $window:ng.IWindowService,
                    private PackageService:main.PackageService,
                    private $q:ng.IQService) {
            // controller init
            AppConfig.then(config => {
                this.transformationPrefix = config.TRANSFORMATION_PREFIX;
                this.packagePrefix = config.PACKAGE_PREFIX;
            });
            this.transformationId = $stateParams.id;
            this.pkg = this.TransformationService.get(this.transformationId);
            this.pkg.then(data => {
                this.transformationObject = data;
                this.name = data.name;
                this.description = data.description;
                this.transformation = data.transformation;
                this.private = data.private;

                this.allowDelete = $auth.isAuthenticated() && data.owner.id === $auth.getPayload().user_id;
                this.selected = {};
            });
            FormatService.getAvailableFormats().then(data => {
                this.availableFormats = this.FormatService.sortByLabel(data.data);
            });
        }

        public isAuthenticated() {
            return this.$auth.isAuthenticated();
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

        public static aceLoaded(editor) {
            odh.main.TransformationService.aceLoaded(editor);
        }

        public preview() {
            this.previewLoading = true;
            this.TransformationService.parse(this.transformation).then((data:any) => {
                angular.forEach(data.data.tables, table => {
                    table.isOwn = this.loadIfPackageUsed(table);
                });
                this.usedTables = data.data.tables;

            });
            this.pkg = this.TransformationService.preview(this.transformation);
        }

        public saveTransformation() {
            this.transformationObject.transformation = this.transformation;
            this.transformationObject.name = this.name;
            this.transformationObject.description = this.description;
            this.transformationObject.put().then(() => {
                this.ToastService.success('Transformation gespeichert');
            }).catch((error) => {
                this.ToastService.failure('Es ist ein Fehler aufgetreten');
                console.error(error);
            });
        }

        public duplicateTransformation() {
            this.TransformationService.description = this.description;
            this.TransformationService.forceManualEdit = true;
            this.TransformationService.transformation = this.transformation;
            this.TransformationService.name = this.name;
            this.$state.go('transformation-create', {
                loadTransformation: true
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
                            this.$state.go('packages')
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

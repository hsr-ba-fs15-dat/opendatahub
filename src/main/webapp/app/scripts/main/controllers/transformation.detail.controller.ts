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
        public loadedTablesArray:any[] = [];
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
        public modifiedTransformation:string;
        public templateTransformation:string;
        public chosenTables:string[] = [];

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
                    private $q:ng.IQService,
                    private $filter:ng.IFilterService) {
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
                this.templateTransformation = data.transformation;
                this.allowDelete = $auth.isAuthenticated() && data.owner.id === $auth.getPayload().user_id;
                this.selected = {};
                this.parse();
            }).catch(
                () => {
                    this.showExpertPanel = true;
                    console.log('error loading pkg');
                }
            );

            FormatService.getAvailableFormats().then(data => {
                this.availableFormats = this.FormatService.sortByLabel(data.data);
            });

        }

        public aceLoaded(editor) {
            odh.main.TransformationService.aceLoaded(editor);
        }

        public isAuthenticated() {
            return this.$auth.isAuthenticated();
        }


        public generateNewTransformation() {
            this.modifiedTransformation = this.templateTransformation;
            this.chosenTables = [];
            angular.forEach(this.selected, (table, tablename) => {
                if (table) {
                    this.chosenTables.push(table.unique_name);
                }
                var i = 0;
                var n = 0;
                do {
                    n = this.modifiedTransformation.search(tablename);
                    if (n !== -1) {
                        var charBefore = this.modifiedTransformation.substr(n - 1, 1);
                        var charAfter = this.modifiedTransformation.substr(n + tablename.length, 1);
                        var quotesUsed = charBefore.match(/['"]/) && charAfter.match(/['"]/);
                        var replacementQuote = quotesUsed ?
                            ('iWillReplaceThis_' + ++i) :
                            this.quote(('iWillReplaceThis_' + ++i));
                        this.modifiedTransformation = this.modifiedTransformation.replace(tablename, replacementQuote);
                    }
                } while (n !== -1);
                for (i; i !== 0; i--) {
                    replacementQuote = 'iWillReplaceThis_' + i;
                    this.modifiedTransformation = this.modifiedTransformation
                        .replace(replacementQuote, table.unique_name);
                }
                this.transformation = this.modifiedTransformation;

            });

        }

        public checkIfOurTable(table:main.ITable) {
            var rxQry = '^({0}|{1})\\d+_.*$'.format(this.packagePrefix, this.transformationPrefix);
            var regEx = new RegExp(rxQry);
            return regEx.test(table.name);
        }

        public loadIfPackageUsed(table:main.ITable) {
            if (this.checkIfOurTable(table)) {
                this.PackageService.getPreviewByUniqueName(table.name, {}).then(result => {
                    console.log(result);
                    if (result) {
                        this.loadedTablesArray.push(result);
                        this.selected[table.name] = result;
                        this.chosenTables.push(table.unique_name);
                        this.generateNewTransformation();
                    }
                });
            }
        }

        public addRemoveTable(table:main.ITable) {
            var index = this.loadedTablesArray.indexOf(table);

            if (index !== -1) {
                this.loadedTablesArray.splice(index);
            } else {
                this.loadedTablesArray.push(table);
            }
        }

        public checkTableSelected(table) {
            /**
             * Checks if the Table is selected.
             * @returns boolean
             */
            return this.loadedTablesArray.indexOf(table) !== -1;
        }

        public preview() {
            this.pkg = this.TransformationService.preview(this.transformation);
        }

        public parse() {
            this.TransformationService.parse(this.transformation).then((data:any) => {
                angular.forEach(data.data.tables, table => {
                    table.isOwn = this.loadIfPackageUsed(table);
                });
                this.usedTables = data.data.tables;
            }).catch(this.displayError);
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

        private displayError(error) {
            console.log(error, '<== display error');
        }

        private quote(field:string) {
            return '"' + field + '"';
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
    export function filterAlreadyAdded() {
        return function (inputArray, filterCriteria) {
            return inputArray.filter(function (item) {
                return filterCriteria.tables.length === 0 || filterCriteria.tables.indexOf(item.unique_name) === -1 ||
                    item.unique_name === filterCriteria.selected;
            });
        };
    }

    angular.module('openDataHub.main')
        .controller('TransformationDetailController', TransformationDetailController)
        .controller('DeleteTransformationController', DeleteTransformationController)
        .filter('filterAlreadyAdded', filterAlreadyAdded);
}

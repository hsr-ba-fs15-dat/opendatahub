/// <reference path='../../all.d.ts' />

module odh.main {
    'use strict';
    export interface IOwner {
        id: number;
        username: string;
        first_name: string;
        last_name: string
    }
    export interface ITransformationObject extends restangular.IElement {
        id: number;
        url: string;
        name: string;
        description: string;
        transformation: string;
        'private': boolean;
        owner: main.IOwner;
        is_template: boolean;
        //preview: string;
        //referenced_transformations: string;
        type: string;
    }
    class TransformationDetailController implements main.ITransformation {
        public pkg:ng.IPromise<ITransformationObject>;
        public name;
        public description;
        public transformationId;
        public transformation;
        public 'private';
        public loadedTablesArray:main.ITable[] = [];
        public usedTables:main.ITable[];
        public selected:any;
        public availableFormats;
        public showExpertPanel = false;
        public allowDelete:boolean;
        public transformationPrefix:string;
        public packagePrefix:string;
        public transformationObject:main.ITransformationObject;
        public modifiedTransformation:string;
        public previewTransformation:string;
        public templateTransformation:string;
        public chosenTables:string[] = [];
        public previewSuccess:boolean = false;

        constructor(private $stateParams:any,
                    private TransformationService:main.TransformationService,
                    private FormatService:odh.main.FormatService,
                    private $state:ng.ui.IStateService,
                    private ToastService:odh.utils.ToastService,
                    private $auth:any,
                    private $modal:ng.ui.bootstrap.IModalService,
                    private AppConfig:odh.IAppConfig,
                    private $window:ng.IWindowService,
                    private PackageService:main.PackageService,
                    private $log:ng.ILogService) {
            // controller init
            AppConfig.then(config => {
                this.transformationPrefix = config.TRANSFORMATION_PREFIX;
                this.packagePrefix = config.PACKAGE_PREFIX;
            });
            this.transformationId = $stateParams.id;
            this.pkg = this.TransformationService.get(this.transformationId);
            console.log(this.pkg);
            this.pkg.then(data => {
                console.log(data);
                this.transformationObject = data;
                this.name = data.name;
                this.description = data.description;
                this.transformation = data.transformation;
                if (!data.is_template) {
                    this.previewTransformation = data.transformation;
                } else {
                    this.showExpertPanel = true;
                }
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

            this.FormatService.getAvailableFormats().then(data => {
                var results = this.FormatService.sortByLabel(data.data);
                results.push({
                    name: null, label: 'Original', description: 'Unveränderte Daten', example: null,
                    extension: null
                });
                this.availableFormats = results;
            });

        }

        public aceLoaded(editor) {
            odh.main.TransformationService.aceLoaded(editor);
        }

        public isAuthenticated() {
            return this.$auth.isAuthenticated();
        }

        /**
         * generates a new Transformation from selected tables
         */
        public generateNewTransformation() {
            var modifiedTransformation = '';
            this.chosenTables = [];
            var selectedTables = [];
            var tableEx = /(?:FROM|JOIN)\s("[^"]*"|\b\w+\b)|("[^"]*"|\b[A-z0-9_]+\b)(?=\.)/ig;
            angular.forEach(this.selected, (table, tablename) => {
                if (table) {
                    this.chosenTables.push(table.unique_name);
                }
                selectedTables.push(tablename);
            });
            var lastIndex = 0;
            var myArray;
            while ((myArray = tableEx.exec(this.templateTransformation)) !== null) {
                var expr = myArray[1] || myArray[2];
                var removedQuotes = 0;
                if (expr.charAt(0) === '"' && expr.charAt(expr.length - 1) === '"') {
                    expr = expr.substr(1, expr.length - 2);
                    removedQuotes += 2;
                }
                var qExpr = expr;
                var getFiltered = (name) => {
                    return this.usedTables.filter((element) => {
                        return element.name === name;
                    });
                };

                if (getFiltered(expr).length > 0) {
                    if (!this.selected[expr]) {
                        qExpr = '{not defined: ' + expr + '}';
                    } else {

                        qExpr = this.selected[expr].unique_name;

                    }
                }
                modifiedTransformation += this.templateTransformation.substr(
                    lastIndex, tableEx.lastIndex - lastIndex - expr.length - removedQuotes
                );
                modifiedTransformation += this.quote(qExpr);
                lastIndex = tableEx.lastIndex;
            }
            modifiedTransformation += this.templateTransformation.substr(lastIndex);

            this.transformation = modifiedTransformation;


        }

        /**
         * checks if the table name is formatted like a ODH table name. (ODHxx_name || TRFxx_name)
         * @param table
         * @returns {boolean}
         */
        public checkIfOurTable(table:main.ITable) {
            var rxQry = '^({0}|{1})\\d+_.*$'.format(this.packagePrefix, this.transformationPrefix);
            var regEx = new RegExp(rxQry);
            return regEx.test(table.name);
        }

        /**
         * Loads a table if its used and named like an ODH table.
         * @param table
         */
        public loadIfPackageUsed(table:main.ITable) {
            if (this.checkIfOurTable(table)) {
                this.PackageService.getPreviewByUniqueName(table.name, {}).then((result:main.ITable) => {
                    if (result) {
                        this.loadedTablesArray.push(result);
                        this.selected[table.name] = result;
                        this.chosenTables.push(table.unique_name);
                    }
                });
            }
        }


        public preview() {
            this.previewTransformation = this.transformation;
        }

        /**
         * loads or unloads a table
         * @param table
         */
        public addRemoveTable(table:main.ITable) {
            var index = this.loadedTablesArray.indexOf(table);

            if (index !== -1) {
                this.loadedTablesArray.splice(index);
            } else {
                this.loadedTablesArray.push(table);
            }
        }

        /**
         * Checks if the Table is selected.
         * @returns boolean
         */
        public checkTableSelected(table) {
            return this.loadedTablesArray.indexOf(table) !== -1;
        }

        public aceBlurred(editor) {
            console.log(editor);
            var val = editor.getEditor().getSession();
            console.log(val);
        }


        public parse() {
            this.TransformationService.parse(this.transformation).then((data:any) => {
                angular.forEach(data.data.tables, table => {
                    table.isOwn = this.loadIfPackageUsed(table);
                });
                this.usedTables = data.data.tables;
            }).catch(() => {
                this.ToastService.failure("Beim parsen ist ein Fehler aufgetreten.")
            });
        }

        public saveTransformation() {
            this.transformationObject.transformation = this.transformation;
            this.transformationObject.name = this.name;
            this.transformationObject.description = this.description;
            this.transformationObject.put().then(() => {
                this.ToastService.success('Transformation gespeichert');
                this.$state.reload();
            }).catch((error) => {
                this.ToastService.failure('Beim Speichern ist ein Fehler aufgetreten');
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

        public downloadAs(group, formatName) {
            this.$log.debug('Triggered download of ', group, 'as', formatName);
            group.canDownload(formatName).then(() => {
                this.$window.location.href = group.data + ( formatName ? '?fmt=' + formatName : '');
            }).catch(() => {
                this.ToastService.failure('Die Datei konnte nicht ins gewünschte Format konvertiert werden.');
            });
        }

        public remove() {
            var modalInstance;
            var odhModal:utils.IOdhModal = {
                buttons: [{
                    text: 'Löschen',
                    cls: 'btn-warning',
                    action: () => {
                        modalInstance.close();
                    }
                },
                    {
                        text: 'Abbrechen',
                        cls: 'btn-primary',
                        action: () => {
                            modalInstance.dismiss();
                        }
                    }],
                question: 'Möchten Sie diese Transformation wirklich löschen?',
                title: 'Sind Sie sicher?'


            };
            modalInstance = this.$modal.open({
                animation: true,
                templateUrl: 'views/helpers/confirmation.html',
                controller: 'ConfirmationController as cc',
                resolve: {
                    odhModal: () => {
                        return odhModal;
                    }

                }
            });
            modalInstance.result.then(result => {
                this.TransformationService.remove({id: this.transformationId}).then(() => {
                        this.$state.go('packages');
                        this.ToastService.failure('Transformation erfolgreich gelöscht');
                    }
                ).catch((err) =>
                        this.ToastService.failure('Beim Löschen der Transformation ist ein Fehler aufgetreten.')
                );
            });
        }

        /**
         * checks if field needs to use quotes (non UTF8 chars)
         * @param field
         * @returns {string}
         */
        private quote(field:string) {
            var regEx = new RegExp('^[A-z_][A-z0-9_]*$');
            if (!regEx.test(field)) {

                return '"' + field + '"';
            }
            return field;
        }
    }

    /**
     * Filters already added tables from assistant
     * @returns {function(any, any): any}
     * @type filter
     */
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
        .filter('filterAlreadyAdded', filterAlreadyAdded);
}

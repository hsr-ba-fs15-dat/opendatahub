/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    /**
     * responsible for creation of transformations.
     * - provides assistant
     * - provides manual editor
     * - saves new transformations
     * - accepts existing transformations for duplication
     */
    export class TransformationCreateController {
        public name:string;
        public description:string;
        public columns:string[];
        public rows:{};
        public types:string[];
        public submitted:boolean = false;
        public documents:Object[];
        public odhqlInputString = '';
        /**
         * ngTableContainer
         */
        public tableParams:any;
        public alerts:Object[] = [];
        public selection:main.ITransformationSelection;
        public quotes = false;
        public forceManualEdit:boolean = false;
        public transformationPreview:string = '';
        public errorMessage;
        public fieldIsModified:boolean = false;
        public tabs:any[] = [];
        public previewObject:any;
        public leaveState = false;
        public transformationPrivate:boolean = false;
        constructor(private $state:ng.ui.IStateService,
                    private ToastService:odh.utils.ToastService,
                    private $log:ng.ILogService,
                    private $auth:any,
                    private TransformationService:main.TransformationService,
                    private TransformationSelection:main.TransformationSelection,
                    private JOIN_OPERATIONS,
                    private $stateParams:{loadTransformation:boolean},
                    private $modal:ng.ui.bootstrap.IModalService,
                    private $scope:any) {
            this.tabs = [
                {
                    heading: 'Start',
                    icon: null,
                    template: 'views/transformation.create/start.html',
                    content: null,
                    active: true,
                    disabled: () => {
                        return false;
                    }
                }, {
                    heading: 'Assistent',
                    icon: 'fa-magic',
                    template: 'views/transformation.create/assistant.html',
                    content: null,
                    active: false,
                    disabled: () => {
                        return false;
                    },
                    open: () => {
                        if (this.forceManualEdit) {
                            var modalInstance:ng.ui.bootstrap.IModalServiceInstance;
                            var odhModal:utils.IOdhModal = {
                                buttons: [{
                                    text: 'OK',
                                    cls: 'btn-warning',
                                    action: () => {
                                        modalInstance.dismiss();
                                    }
                                },
                                    {
                                        text: 'Abbrechen',
                                        cls: 'btn-primary',
                                        action: () => {
                                            modalInstance.close(1);
                                        }
                                    }],
                                question: 'Sie haben manuelle Änderungen am Query vorgenommen. Wenn Sie den ' +
                                'Assistenten erneut ausführen gehen diese ' +
                                '<strong>unwiderruflich</strong> verloren! <br/><br/> Möchten Sie wirklich fortfahren?',
                                title: 'Assistent blockiert!'


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
                                if (result === 1) {
                                    this.tabs[2].active = true;
                                }
                            });
                        }

                    }
                }, {
                    heading: 'Manuelles Bearbeiten',
                    icon: 'fa-pencil',
                    template: 'views/transformation.create/manual.html',
                    content: null,
                    active: false,
                    disabled: () => {
                        return false;
                    }
                }

            ];
            if ($stateParams.loadTransformation) {
                this.name = TransformationService.name;
                this.description = TransformationService.description;
                this.odhqlInputString = TransformationService.transformation;
                this.forceManualEdit = TransformationService.forceManualEdit;
                this.tabs[2].active = true;
            }

            this.selection = TransformationSelection;
            this.$scope.$on('$stateChangeStart',
                (event, toState, toParams, fromState, fromParams) => {
                    if (this.odhqlInputString) {
                        if (!this.leaveState) {
                            event.preventDefault();
                            var modalInstance:ng.ui.bootstrap.IModalServiceInstance;
                            var odhModal:utils.IOdhModal = {
                                buttons: [{
                                    text: 'OK',
                                    cls: 'btn-warning',
                                    action: () => {
                                        modalInstance.close(1);
                                    }
                                },
                                    {
                                        text: 'Abbrechen',
                                        cls: 'btn-primary',
                                        action: () => {
                                            modalInstance.dismiss();
                                        }
                                    }],
                                question: 'Sie haben nicht gespeicherte Änderungen. ' +
                                'Wenn Sie fortfahren gehen diese verloren!<br/><br/> Möchten Sie wirklich fortfahren?',
                                title: 'Änderungen gehen verloren!'


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
                                if (result === 1) {
                                    this.leaveState = true;
                                    this.$state.go(toState.name);
                                }
                            });
                        }


                    }
                });
        }

        public switchTab(tab:string) {
            switch (tab) {
                case 'manual':
                    this.tabs[2].active = true;
                    break;
                case 'assistant':
                    this.tabs[1].active = true;
                    break;
                case 'start':
                    this.tabs[0].active = true;
                    break;
            }
        }

        public aceLoaded(editor) {
            odh.main.TransformationService.aceLoaded(editor);
        }

        public lockAssistant(lock = true) {
            this.forceManualEdit = lock;
        }

        public getJoinOperations() {
            return this.JOIN_OPERATIONS;
        }

        public addRemoveField(col, table:main.ITable) {
            this.selection.addRemoveField(col, table);
            this.generate();
        }

        public manualChange() {
            this.lockAssistant();
            this.fieldIsModified = true;
            this.previewObject = null;
        }

        public toggleQuote(value:boolean) {
            if (value !== undefined) {
                this.TransformationSelection.setQuotes(value);
            }
            return this.TransformationSelection.getQuotes();
        }

        public joinOperation(table) {
            return this.selection.getJoinOperation(table);
        }

        public addField(col, table:main.ITable) {
            this.selection.addField(col, table);
            this.generate();
        }

        public generate() {
            this.fieldIsModified = false;
            this.previewObject = null;
            this.forceManualEdit = false;
            this.odhqlInputString = this.selection.generateTransformation();
        }

        public getTableByName(tableName:string) {
            return this.selection.getTableByName(tableName);
        }

        public getFields(tableName:any) {
            if (typeof tableName === 'string') {
                return this.selection.getFields(tableName);
            }
            if (typeof tableName === 'object') {
                return this.selection.getFields(tableName.uniqueId);
            }
        }

        public getSelectedFields(table:main.ITable) {
            if (table) {
                return this.selection.getSelectedFields(table);
            }
        }

        public allTables() {
            return this.selection.allTables();
        }

        public closeAlert(index) {
            this.alerts.splice(index, 1);
        }

        public addRemoveTable(table) {
            this.selection.addRemoveTable(table);
        }

        public checkTableSelected(table) {
            return this.selection.tableSelected(table);
        }

        public preview() {

            this.previewObject = null;
            this.transformationPreview = this.odhqlInputString;
            this.fieldIsModified = false;
        }

        public cancel() {
            this.$state.go('main');
        }

        public isAuthenticated() {
            return this.$auth.isAuthenticated();
        }

        public isPrivate(priv:boolean):boolean {
            if (priv !== undefined) {
                this.transformationPrivate = priv;
            }
            return this.selection.isPrivate() || this.transformationPrivate;
        }

        public submit() {

            this.submitted = true;
            var transformation:main.ITransformation;
            transformation = {
                name: this.name,
                description: this.description,
                transformation: this.odhqlInputString,
                'private': this.isPrivate(this.transformationPrivate),
                file_groups: this.selection.getFileGroups()
            };
            var promise = this.TransformationService.post(transformation);
            promise.then(data => this.createSuccess(data))
                .catch(data => this.createFailure(data));

        }

        private createSuccess(data) {
            this.leaveState = true;
            this.$state.go('transformation-detail', {id: data.id});
            this.ToastService.success('Ihre Daten wurden gespeichert ');
        }

        private createFailure(data) {
            this.ToastService.failure('Es ist ein Fehler aufgetreten!');
            this.$log.error(data);
        }

    }
    angular.module('openDataHub.main').controller('TransformationCreateController', TransformationCreateController);

}

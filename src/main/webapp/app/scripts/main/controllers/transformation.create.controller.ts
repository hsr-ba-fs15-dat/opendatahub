/// <reference path='../../all.d.ts' />


module odh {
    'use strict';
    interface IField {
        name: string;
        alias: string;
    }

    interface IExpression {
        foreignKey: IField;
        joinField: IField;
        joinTable: any;
        operation: any;
    }
    export class TransformationCreateController {
        public name:string;
        public description:string;
        public query:string;
        public columns:string[];
        public rows:{};
        public types:string[];
        public submitted:boolean = false;
        public documents:Object[];
        public odhqlInputString = '';
        public manualEdit:boolean = false;
        public count:number = 3;
        public editor:any;
        public tableParams:any;
        public alerts:Object[] = [];
        public selection:main.ITransformationSelection;
        public quotes = true;
        public useAsTemplate:boolean = false;
        public fileGroupTable;
        public forceManualEdit:boolean = false;
        constructor(private $state:ng.ui.IStateService, private $scope:any,
                    private ToastService:odh.utils.ToastService,
                    private FileGroupService:main.FileGroupService,
                    private $log:ng.ILogService, private ngTableParams,
                    private $auth:any, private TransformationService:main.TransformationService,
                    private TransformationSelection:main.TransformationSelection, private JOIN_OPERATIONS,
                    private $stateParams:{loadTransformation:boolean}) {

            if ($stateParams.loadTransformation) {
                this.name = TransformationService.name;
                this.description = TransformationService.description;
                this.manualEdit = true;
                this.odhqlInputString = TransformationService.transformation;
                this.forceManualEdit = TransformationService.forceManualEdit;
            }

            this.selection = angular.copy(TransformationSelection);
            this.fileGroupTable = new ngTableParams({
                    page: 1,
                    count: 10
                }, {
                    counts: [],
                    total: 0,
                    getData: ($defer, params) => {
                        params.total(this.selection.allTables().length);
                        $defer.resolve(this.selection.allTables());

                    }
                }
            );
        }


        public transformation(newInput:string = '') {
            if (newInput && this.manualEdit) {
                this.forceManualEdit = true;
                this.odhqlInputString = newInput;
            }
            if (!this.manualEdit) {
                this.odhqlInputString = this.selection.generateTransformation();
            }
            return this.odhqlInputString;
        }

        public aceLoaded(editor) {
            editor.$blockScrolling = 'Infinity';
            var _renderer = editor.renderer;
            var _session = editor.getSession();
            _session.setOptions({mode: 'ace/mode/sql'});
            _renderer.setOptions({
                maxLines: Infinity,
                theme: 'twilight'
            });
            editor.setOptions({
                showGutter: true,
                firstLineNumber: 1
            });

        }

        public getJoinOperations() {
            return this.JOIN_OPERATIONS;
        }

        public addRemoveField(col, table:main.ITable) {
            if (!this.manualEdit) {
                this.selection.addRemoveField(col, table);
            }
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

        public increaseTablePreview(group) {
            this.FileGroupService.getPreview(group, group.preview.count += 3);
        }

        public toggleManualEdit() {
            this.manualEdit = !this.manualEdit;
        }

        public addRemoveTable(table) {
            this.selection.addRemoveTable(table);
        }

        public checkTableSelected(table) {
            return this.selection.tableSelected(table);
        }

        public useQuotes(checkbox) {
            console.log(checkbox);
            this.selection.toggleQuotes();
        }

        public preview() {
            var defer;
            if (this.useAsTemplate) {
                defer = this.TransformationService.parse(this.transformation());
            } else {
                defer = this.TransformationService.preview(this.transformation());
            }
            defer.then((data:any) => {
                if (this.useAsTemplate) {
                    this.ToastService.success('Query ist in Ordnung');
                } else {
                    this.columns = data.data.columns;
                    this.rows = data.data.data;
                    this.types = data.data.types;
                }
            }).catch((data:any) => {
                if (typeof data === 'object') {
                    data = data.data;
                    this.alerts.pop();
                    if (data.type === 'parse') {
                        this.alerts.push({
                            msg: 'Parse Fehler (' + data.lineno + ':' + data.col + ') Line: ' + data.line,
                            type: 'danger',
                            title: 'Fehler:'
                        });

                    }

                    if (data.type === 'execution') {
                        this.alerts.push({
                            msg: 'Ausführungs Fehler: ' + data.error,
                            type: 'danger',
                            title: 'Fehler:'
                        });
                    }
                }

                this.ToastService.failure(
                    'Es ist ein Fehler aufgetreten!');
            });
        }

        public cancel() {
            this.$state.go('main');
        }

        public isAuthenticated() {
            return this.$auth.isAuthenticated();
        }

        public isPrivate():boolean {
            return this.selection.isPrivate();
        }

        public joinOperation(table) {
            return this.selection.getJoinOperation(table);
        }

        public submit() {
            this.submitted = true;
            var defer;
            if (this.useAsTemplate) {
                defer = this.TransformationService.parse(this.transformation());
            } else {
                defer = this.TransformationService.preview(this.transformation());
            }
            defer.then(() => {
                var transformation:main.ITransformation;
                transformation = {
                    name: this.name,
                    description: this.description,
                    transformation: this.odhqlInputString,
                    'private': this.isPrivate(),
                    file_groups: this.selection.getFileGroups()
                };
                var promise = this.TransformationService.post(transformation);
                promise.then(data => this.createSuccess(data))
                    .catch(data => this.createFailure(data));
            });
        }

        private createSuccess(data) {
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

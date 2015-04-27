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

        constructor(private $http:ng.IHttpService, private $state:ng.ui.IStateService, private $scope:any,
                    private ToastService:odh.utils.ToastService, private $window:ng.IWindowService, private $upload,
                    private UrlService:odh.utils.UrlService, private FileGroupService:main.FileGroupService,
                    private DocumentService:main.DocumentService,
                    private $log:ng.ILogService, private ngTableParams, public $filter:ng.IFilterService,
                    private $auth:any, private TransformationService:main.TransformationService,
                    private TransformationSelection:main.TransformationSelection, private JOIN_OPERATIONS) {

            this.tableParams = new ngTableParams({
                page: 1,            // show first page
                count: 10,           // count per page
                limit: 10
            }, {
                counts: [10, 25, 50, 100],
                total: 0, // length of data
                getData: ($defer, params) => {
                    DocumentService.getList(params.url()).then(result => {
                        params.total(result.count);
                        $defer.resolve(result.results);
                    });
                }
            });

            this.selection = angular.copy(TransformationSelection);

        }

        public getFileGroup(document, count = 3) {
            this.FileGroupService.getAll(document.id, true, count).then(filegroups => {
                if (!document.$showRows) {
                    angular.forEach(filegroups, (fg) => {
                        angular.forEach(fg.preview, (preview) => {
                            preview.cols = [];
                            preview.parent = fg.id;
                            preview.private = document.private;
                            angular.forEach(preview.columns, (col) => {
                                preview.cols.push({name: col, alias: col, type: preview.types[col]});
                            });
                        });
                    });
                    document.fileGroup = filegroups;
                } else {
                    document.fileGroup = [];
                }
                document.$showRows = !document.$showRows;
            }).catch(error => this.ToastService.failure('Es ist ein Fehler aufgetreten.'));
        }

        public transformation(newInput:string = '') {
            if (newInput && this.manualEdit) {
                this.odhqlInputString = newInput;
                return newInput;
            }
            if (!this.manualEdit) {
                this.odhqlInputString = this.selection.generateTransformation();
            }
            return this.odhqlInputString;
        }

        public aceLoaded(editor) {
            editor.$blockScrolling = 'Infinity';
            editor.setOptions({
                maxLines: Infinity
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

        public getFields(tableName:string) {
            return this.selection.getFields(tableName);
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
                }
            }).catch((data:any) => {
                console.log(data);
                if (typeof data === 'object') {
                    data = data.data;
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

        public execute() {
            this.$http.get(this.UrlService.get('odhql'), {params: {query: this.query}}).then((data:any) => {
                this.columns = data.data.columns;
                this.rows = data.data.data;
            });
        }

        public isPrivate():boolean {
            return this.selection.isPrivate();
        }

        public joinOperation(table) {
            return this.selection.getJoinOperation(table);
        }

        public submit() {
            this.submitted = true;
            this.$scope.form.$setDirty();
            this.TransformationService.preview(this.transformation()).then(() => {
                if (this.$scope.form.$invalid) {
                    return;
                }
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
            }).catch(() => {
                this.$scope.form.odhqlinput.$setValidity('required', false);
            });
        }

        private createSuccess(data) {
            this.$state.go('transformation.detail', {id: data.id});
            this.ToastService.success('Ihre Daten wurden gespeichert ');
        }

        private createFailure(data) {
            this.ToastService.failure('Es ist ein Fehler aufgetreten!');
            this.$log.error(data);
        }

    }
    angular.module('openDataHub.main').controller('TransformationCreateController', TransformationCreateController);

}

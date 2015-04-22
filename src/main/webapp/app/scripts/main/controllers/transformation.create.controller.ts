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
        public selected;
        public manualEdit:boolean = false;
        public count:number = 3;
        public useQuotes:boolean = true;
        public joinOperations:{
            none: {}
            union: {}
            join: {}
        };
        public editor:any;
        public tableParams:any;
        public alerts:Object[] = [];

        constructor(private $http:ng.IHttpService, private $state:ng.ui.IStateService, private $scope:any,
                    private ToastService:odh.utils.ToastService, private $window:ng.IWindowService, private $upload,
                    private UrlService:odh.utils.UrlService, private FileGroupService:main.FileGroupService,
                    private DocumentService:main.DocumentService,
                    private $log:ng.ILogService, private ngTableParams, public $filter:ng.IFilterService,
                    private $auth:any, private TransformationService:main.TransformationService) {

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

            this.selected = {
                fileGroups: [],
                items: [],
                fields: {},
                expression: {},
                unionTargets: [],
                joinTargets: [],
                remove: (item) => {
                    var index = this.selected.items.indexOf(item);
                    if (index > -1) {
                        this.selected.items.splice(index, 1);
                    }
                    delete this.selected.fields[item.uniqueid];
                    delete this.selected.expression[item.uniqueid];
                    this.selected.fileGroups.splice(this.selected.fileGroups.indexOf(item.parent), 1);
                },
                add: (item) => {
                    if (this.selected.items.indexOf(item) === -1) {
                        item.uniqueid = item.name;
                        item.uniqueidAlias = item.name;
                        this.selected.expression[item.uniqueid] = {};
                        this.selected.items.push(item);
                        this.selected.expression[item.uniqueid].operation = this.joinOperations.none;
                        this.selected.fileGroups.push(item.parent);
                    }
                },
                addRemove: (item) => {
                    var index = this.selected.items.indexOf(item);
                    if (index === -1) {
                        this.selected.add(item);
                    } else {
                        this.selected.remove(item);

                    }
                },
                getItem: (item) => {
                    for (var i = 0; i < this.selected.items.length; i++) {
                        if (this.selected.items[i].uniqueid === item) {
                            return this.selected.items[i];
                        }
                    }
                }
            };
            this.joinOperations = {

                none: {
                    label: 'Nein',
                    operation: null
                },
                union: {
                    label: 'per UNION',
                    operation: 'union'
                },
                join: {
                    label: 'per JOIN',
                    operation: 'join'
                }
            };

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
                var fields:string[] = [];
                var master:string = '';
                var joinStatements:string[];
                var unionStatements:string[];
                unionStatements = [];
                joinStatements = [];

                this.selected.joinTargets = [];

                angular.forEach(this.selected.expression, (value:IExpression, key:string) => {

                    if (!value.operation.operation) {
                        if (!master) {
                            fields = this.createFieldNames(this.selected.fields[key], key).concat(fields);
                            master = key;
                            this.selected.joinTargets.push(this.selected.getItem(key));

                        }

                    }
                    if (value.operation.operation === 'union') {
                        this.selected.joinTargets.push(this.selected.getItem(key));
                        var unionFields = this.createFieldNames(this.selected.fields[key], key);
                        unionStatements.push(' \nUNION \n SELECT '.concat(unionFields.join(',\n'),
                            ' FROM "', key + '"'));
                    }
                    if (value.operation.operation === 'join') {
                        this.selected.joinTargets.push(this.selected.getItem(key));

                        if (value.foreignKey) {
                            fields = this.createFieldNames(this.selected.fields[key], key).concat(fields);
                            joinStatements.push(
                                ' JOIN '.concat(
                                    this.quote(key),
                                    ' on ',
                                    this.createFieldNames([value.foreignKey], value.joinTable.uniqueid, true)[0],
                                    ' = ',
                                    this.createFieldNames([value.joinField], key, true)[0]
                                )
                            );
                        }


                    }

                });
                if (master && fields) {
                    this.odhqlInputString = 'SELECT '.concat(
                        fields.join(',\n'),
                        ' \nFROM ',
                        this.quote(master),
                        ' \n',
                        joinStatements.join(' \n '),
                        unionStatements.join(' \n')
                    );
                }
            }
            return this.odhqlInputString;
        }

        public addFields(group) {
            if (!this.manualEdit) {
                angular.forEach(group.cols, (col) => {
                    this.selected.fields[group.uniqueid].push(col);
                });
            }
        }

        public aceLoaded(editor) {
            editor.$blockScrolling = 'Infinity';
        }

        public addField(col, group) {
            if (!this.manualEdit) {
                this.selected.fields[group.uniqueid] = this.selected.fields[group.uniqueid] || [];
                var index = this.selected.fields[group.uniqueid].indexOf(col);
                if (index > -1) {
                    this.selected.fields[group.uniqueid].splice(index, 1);
                } else {
                    this.selected.fields[group.uniqueid].push(col);
                }
            }
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

        public preview() {
            var defer = this.TransformationService.preview(this.transformation());
            defer.then((data:any) => {
                this.columns = data.data.columns;
                this.rows = data.data.data;
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
            var isPrivate:boolean = false;
            angular.forEach(this.selected.items, (item) => {
                if (!isPrivate) {
                    if (item.private) {
                        isPrivate = true;
                    }
                }
            });
            return isPrivate;
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
                    file_groups: this.selected.fileGroups
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
            this.ToastService.failure('Es ist ein Fehler aufgetreten!')
            this.$log.error(data);
        }

        private createFieldNames(fields:IField[], group:string, doNotCheckAlias:boolean = false):string[] {
            var newFields = [];
            angular.forEach(fields, (field) => {
                newFields.push(
                    [this.quote(group), (field.name === field.alias || doNotCheckAlias)
                        ? this.quote(field.name) : [this.quote(field.name), this.quote(field.alias)].join(' AS ')]
                        .join('.'));
            });
            return newFields;
        }

        private quote(field:string) {
            if (this.useQuotes) {

                return '"' + field + '"';
            }
            return field;
        }

    }
    angular.module('openDataHub.main').controller('TransformationCreateController', TransformationCreateController);

}

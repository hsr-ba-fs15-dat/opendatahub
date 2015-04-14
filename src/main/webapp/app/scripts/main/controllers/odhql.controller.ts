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
    export class OdhQLController {

        public query:string;
        public columns:string[];
        public rows:{};
        public submitted:boolean = false;
        public documents:Object[];
        public odhqlInputString = '';
        public selected;
        public manualEdit:boolean = false;
        public joinOperations:{
            none: {}
            union: {}
            join: {}
        };
        public tableParams:any;
        public alerts:Object[] = [];

        constructor(private $http:ng.IHttpService, private $state:ng.ui.IStateService, private $scope:any,
                    private ToastService:odh.utils.ToastService, private $window:ng.IWindowService, private $upload,
                    private UrlService:odh.utils.UrlService, private FileGroupService:main.FileGroupService,
                    private DocumentService:main.DocumentService,
                    private $log:ng.ILogService, private ngTableParams, public $filter:ng.IFilterService,
                    private $auth:any) {

            this.tableParams = new ngTableParams({
                page: 1,            // show first page
                count: 10,           // count per page
                limit: 10
            }, {
                counts: [10, 25, 50, 100],
                total: 0, // length of data
                getData: ($defer, params) => {
                    DocumentService.getList(params.url()).then(result => {
                        console.log(params);
                        params.total(result.count);
                        $defer.resolve(result.results);
                    });
                }
            });

            this.selected = {
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
                    this.selected.fields[item.uniqueid] = [];
                }

                ,
                add: (item) => {
                    if (this.selected.items.indexOf(item) === -1) {
                        item.uniqueid = 'ODH' + item.id;
                        this.selected.expression[item.uniqueid] = {};
                        this.selected.items.push(item);
                        this.selected.expression[item.uniqueid].operation = this.joinOperations.none;
                    }
                }
                ,
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

        public getFileGroup(document) {
            this.FileGroupService.getAll(document.id, true).then(filegroups => {

                document.$showRows = !document.$showRows;
                if (document.$showRows) {
                    angular.forEach(filegroups, (fg) => {
                        fg.cols = [];
                        angular.forEach(fg.preview.columns, (col) => {
                            fg.cols.push({name: col, alias: col});
                        });
                    });
                    document.fileGroup = filegroups;

                } else {
                    document.fileGroup = [];
                }
            });
        }


        public odhqlInput(newInput:string = '') {
            if (newInput) {
                this.manualEdit = true;
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
                angular.forEach(this.selected.expression, (value:IExpression, key) => {
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
                            ' FROM ', key));
                    }
                    if (value.operation.operation === 'join') {
                        this.selected.joinTargets.push(this.selected.getItem(key));

                        if (value.foreignKey) {
                            fields = this.createFieldNames(this.selected.fields[key], key)
                                .concat(fields);
                            joinStatements.push(
                                ' JOIN '.concat(
                                    key,
                                    ' on ',
                                    this.createFieldNames([value.foreignKey], value.joinTable.uniqueid, true)[0],
                                    ' = ',
                                    this.createFieldNames([value.joinField], key, true)[0]
                                )
                            );
                        }


                    }

                });

                this.odhqlInputString = 'SELECT '.concat(
                    fields.join(',\n'),
                    ' \nFROM ',
                    master,
                    ' \n',
                    joinStatements.join(' \n '),
                    unionStatements.join(' \n')
                );
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

        public preview() {
            this.$http.get(this.UrlService.get('odhql'), {
                params: {
                    query: this.odhqlInput()
                        .replace(/(\r\n|\n|\r|\t)/gm, '')
                }
            }).then((data:any) => {
                this.columns = data.data.columns;
                this.rows = data.data.data;
            }).catch((data:any) => {
                data = data.data.split('\n');
                this.ToastService.failure(
                    'Es ist ein Fehler aufgetreten! (Fehlermeldung in der Konsole ersichtlich.) ' + data[1]);
                this.alerts.push({msg: data.slice(0, 3).join('\n'), type: 'danger', title: 'Fehler:'});
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

        private createFieldNames(fields:IField[], group:string, doNotCheckAlias:boolean = false):string[] {
            var newFields = [];
            angular.forEach(fields, (field) => {
                newFields.push([group, (field.name === field.alias || doNotCheckAlias)
                    ? field.name : [field.name, field.alias].join(' AS ')]
                    .join('.'));
            });
            return newFields;
        }

    }
    angular.module('openDataHub.main').controller('OdhQLController', OdhQLController);

}

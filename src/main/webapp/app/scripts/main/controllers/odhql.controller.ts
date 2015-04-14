/// <reference path='../../all.d.ts' />


module odh {
    'use strict';
    interface Field {
        name: string;
        alias: string;
    }

    interface IExpression {
        foreignKey: Field;
        joinField: Field;
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
        public joinOperations:{};
        public tableParams:any;

        constructor(private $http:ng.IHttpService, private $state:ng.ui.IStateService, private $scope:any,
                    private ToastService:odh.utils.ToastService, private $window:ng.IWindowService, private $upload,
                    private UrlService:odh.utils.UrlService, private FileGroupService:main.FileGroupService,
                    private DocumentService:main.DocumentService,
                    private $log:ng.ILogService, private ngTableParams, public $filter:ng.IFilterService) {

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
                        this.selected.expression[item.uniqueid].operation = this.joinOperations['none'];
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


                var connector = '';
                var fields:string[] = [];
                var master:string = '';
                var joinStatement:string = '';
                var joinStatements:string[];
                joinStatements = [];
                this.selected.joinTargets = [];
                angular.forEach(this.selected.expression, (value:IExpression, key) => {
                    if (!value.operation.operation) {
                        if (!master) {
                            fields = this.createFieldNames(this.selected.fields[key], key).concat(fields);
                            master = key;
                        }
                        this.selected.joinTargets.push(this.selected.getItem(key));
                        console.log(this.selected.joinTargets, 't');

                    }
                    if (value.operation.operation == 'union') {

                    }
                    if (value.operation.operation == 'join') {

                        if (value.foreignKey) {
                            fields = this.createFieldNames(this.selected.fields[key], key)
                                .concat(fields);
                            joinStatements.push(
                                ' JOIN '.concat(
                                    key,
                                    ' on ',
                                    this.createFieldNames([value.foreignKey], value.joinTable.uniqueid, false)[0],
                                    ' = ',
                                    this.createFieldNames([value.joinField], key, false)[0]
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
                    joinStatements.join(' \n')
                );
                return this.odhqlInputString;
            }
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

        public preview() {
            this.$http.get(this.UrlService.get('odhql'), {
                params: {
                    query: this.odhqlInput()
                        .replace(/(\r\n|\n|\r|\t)/gm, '')
                }
            }).then((data:any) => {
                this.columns = data.data.columns;
                this.rows = data.data.data;
            });
        }

        public cancel() {
            this.$state.go('main');
        }

        public execute() {
            this.$http.get(this.UrlService.get('odhql'), {params: {query: this.query}}).then((data:any) => {
                this.columns = data.data.columns;
                this.rows = data.data.data;
            });
        }

        private createFieldNames(fields:Field[], group:string, checkAlias:boolean = true):string[] {
            var newFields = [];
            angular.forEach(fields, (field) => {
                newFields.push([group, (field.name === field.alias && checkAlias) ? field.name : [field.name, field.alias].join(' AS ')]
                    .join('.'));
            });
            return newFields;
        }

    }
    angular.module('openDataHub.main').controller('OdhQLController', OdhQLController);

}

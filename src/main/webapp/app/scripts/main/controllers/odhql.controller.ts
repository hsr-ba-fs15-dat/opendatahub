/// <reference path='../../all.d.ts' />


module odh {
    'use strict';

    export class OdhQLController {

        public query:string;
        public columns:string[];
        public rows:{};
        public submitted:boolean = false;
        public fg;
        public fileGroups;
        public odhqlInputString = '';
        public uniqueName;
        public items;
        public selected;
        public manualEdit:boolean = false;
        public joinOperations:{};
        public joinOperationsSelection:any = [];
        public join_fields:any;
        public tableParams:any;

        constructor(private $http:ng.IHttpService, private $state:ng.ui.IStateService, private $scope:any,
                    private ToastService:odh.utils.ToastService, private $window:ng.IWindowService, private $upload,
                    private UrlService:odh.utils.UrlService, private FileGroupService:main.FileGroupService,
                    private $log:ng.ILogService, private ngTableParams, public $filter:ng.IFilterService) {
            var fg = {};
            var fileGroups = [];

            FileGroupService.getAll(false, false).then(res => {
                angular.forEach(res, (value) => {
                    if (fg[value.document.id] === undefined) {
                        fg[value.document.id] = [value.document];
                    }
                    fg[value.document.id].push(value);
                    console.log(value);
                    value.documentId = value.document.id;
                    value.file_name = value.files[0].file_name;
                    fileGroups.push(value);
                    console.log('fg', fileGroups);
                });
                this.items = fg;
                this.tableParams = new ngTableParams({
                    page: 1,            // show first page
                    count: 10           // count per page
                }, {
                    groupBy: 'documentId',
                    total: fileGroups.length, // length of data
                    getData: ($defer, params) => {
                        var orderedData = params.sorting() ?
                            $filter('orderBy')(fileGroups, this.tableParams.orderBy()) : fileGroups;
                        orderedData = params.filter ? $filter('filter')(orderedData, params.filter()) : orderedData;
                        $defer.resolve(
                            orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count())
                        );
                    }
                });
            });
            this.selected = {
                items: [],
                fields: {},
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
                        item.cols = [];
                        this.FileGroupService.getPreview(item).then(data => {
                            item.preview = data.data;
                            angular.forEach(item.preview.columns, (col) => {
                                item.cols.push({name: col, alias: col});
                            });
                        });
                        item.uniqueid = 'ODH' + item.id;
                        this.selected.items.push(item);
                    }
                }
            };
            this.joinOperations = {
                union: {
                    label: 'UNION'
                },
                join: {
                    label: 'JOIN'
                }
            };

        }


        public odhqlInput(newInput:string = '') {
            var odhql = [];
            if (newInput) {
                this.manualEdit = true;
                this.odhqlInputString = newInput;
                return newInput;
            }
            if (!this.manualEdit) {
                var connector = '';
                angular.forEach(this.selected.fields, (value, key) => {
                    if (this.joinOperationsSelection[key]) {
                        connector = this.joinOperationsSelection[key].label;
                    }
                    var fields = [];
                    angular.forEach(value, (col) => {
                        if (col.alias !== col.name) {
                            fields.push(key + '.' + col.name + ' AS ' + col.alias);
                        } else {
                            fields.push([key, col.name].join('.'));
                        }
                    });
                    if (fields.length > 0) {
                        var statement = '';
                        if (connector !== 'JOIN') {
                            statement += 'SELECT \n\t' + fields.join(',\n\t') + '\n FROM ' + key;
                        }
                        if (connector === 'JOIN') {
                            statement += key;
                            statement += ' ON ';
                            var join = [];
                            angular.forEach(this.join_fields[key], (joinValue, joinKey) => {

                                var join_expression = joinKey;
                                join_expression += '.';
                                join_expression += joinValue.name;
                                join.push(join_expression);
                            });
                            statement += join.join(' = ');
                            statement += ' \n';

                        }
                        odhql.push(statement);
                    }


                });
                this.odhqlInputString = odhql.join('\n ' + connector + ' \n');
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

    }
    angular.module('openDataHub.main').controller('OdhQLController', OdhQLController);

}
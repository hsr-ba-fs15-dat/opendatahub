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
        public odhsqlinput = '';
        public uniqueName;
        public items;
        public selected;

        constructor(private $http:ng.IHttpService, private $state:ng.ui.IStateService, private $scope:any,
                    private ToastService:odh.utils.ToastService, private $window:ng.IWindowService, private $upload,
                    private UrlService:odh.utils.UrlService, private FileGroupService:main.FileGroupService,
                    private $log:ng.ILogService) {
            var fg = {};
            FileGroupService.getAll(false, true).then(res => {
                angular.forEach(res, (value) => {
                    if (fg[value.document.id] === undefined) {
                        fg[value.document.id] = [value.document];
                    }
                    fg[value.document.id].push(value);
                });
                this.items = fg;
            });
            this.selected = {
                items: [],
                fields: {},
                remove: (item) => {
                    var index = this.selected.items.indexOf(item);
                    if (index > -1) {
                        this.selected.items.splice(index, 1);
                    }
                }

                ,
                add: (item) => {
                    if (this.selected.items.indexOf(item) === -1) {
                        item.uniqueid = 'ODH' + item.id;
                        item.cols = [];
                        angular.forEach(item.preview.columns, (col) => {
                            item.cols.push({name: col, alias: col});
                        });
                        console.log('cols:', item.cols);
                        this.selected.items.push(item);
                    }
                }
            };
        }

        public odhqlInput() {
            var odhql = [];
            angular.forEach(this.selected.fields, (value, key) => {
                var fields = [];
                angular.forEach(value, (col) => {
                    if (col.alias !== col.name) {
                        fields.push(key + '.' + col.name + ' AS ' + col.alias);
                    } else {
                        fields.push([key, col.name].join('.'));
                    }
                });
                odhql.push('SELECT ' + fields.join(',') + ' FROM ' + key);

            });
            return odhql.join(' UNION ');
        }

        public addFields(group) {
            angular.forEach(group.cols, (col) => {
                this.selected.fields[group.uniqueid].push(col);
            });
        }

        public addField(col, group) {
            this.selected.fields[group.uniqueid] = this.selected.fields[group.uniqueid] || [];
            var index = this.selected.fields[group.uniqueid].indexOf(col);
            if (index > -1) {
                this.selected.fields[group.uniqueid].splice(index, 1);
            } else {

                this.selected.fields[group.uniqueid].push(col);
            }
        }

        public preview() {
            this.$http.get(this.UrlService.get('odhql'), {params: {query: this.odhqlInput()}}).then((data:any) => {
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

/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    class OdhqlSelectController {

        public items:{};
        public selected:{};
        public searchField:string;

        constructor(private $modal, private $log, private DocumentService:DocumentService, private FileGroupService:FileGroupService) {
            // controller init
            var fg = {};
            FileGroupService.getAll(false, true).then(res => {
                angular.forEach(res, (value, key) => {
                    console.log(value.document, key);
                    if (fg[value.document.id] == undefined) {
                        fg[value.document.id] = [value.document];
                    }
                    fg[value.document.id].push(value);
                });
                this.items = fg;
                console.debug('Gathered FileGroups', fg);
            });
            this.$log.debug(this.items);
        }

        public open() {
            console.log(this.items);
            var modalInstance = this.$modal.open({
                templateUrl: 'odhql-source-select.html',
                controller: 'odhqlSelectInstanceController as IOdh',
                size: 'lg',
                resolve: {
                    items: () => {
                        return this.items;
                    },
                    selected: () => {
                        return this.selected;
                    }
                }
            });

            modalInstance.result.then((selectedItem) => {
                this.selected = selectedItem;
            }, () => {
                this.$log.info('Modal dismissed at: ' + new Date());
            });
        }


    }


    class OdhqlSelectInstanceController {
        public selectedGrid:any;

        constructor(private $modalInstance, private items, private selected) {
            this.selected = {
                items: selected || [],
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
                        item.uniqueid = 'odh_' + 'fg_' + item.id;
                        this.selected.items.push(item);
                    }
                }
            };
        }
        public addFields(group){
            this.selected.fields[group.id] = [];
            this.selected.fields[group.id].push(group.preview.columns[0]);
            console.log(group.preview.columns[0]);
        }
        public addField(col, group, ele) {
            console.log(ele);
            this.selected.fields[group.id] = this.selected.fields[group.id] || [];
            var index = this.selected.fields[group.id].indexOf(col);
            if (index > -1) {
                this.selected.fields[group.id].splice(index, 1);
            } else {

                this.selected.fields[group.id].push(col);
            }
            console.log(this.selected.fields);
        }

        public ok() {
            this.$modalInstance.close(this.selected.items);
        }

        public cancel() {
            this.$modalInstance.dismiss('cancel');
        }
    }

    angular.module('openDataHub.main').controller('odhqlSelectController', OdhqlSelectController);
    angular.module('openDataHub.main').controller('odhqlSelectInstanceController', OdhqlSelectInstanceController);
}

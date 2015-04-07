/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    class OdhqlSelectController {

        public items:{};
        public selected:{};

        constructor(private $modal, private $log, private DocumentService:DocumentService) {
            // controller init
            this.items = DocumentService.getAll();
            this.$log.debug(this.items);
        }


        public open() {
            var modalInstance = this.$modal.open({
                templateUrl: 'odhql-source-select.html',
                controller: 'odhqlSelectInstanceController as IOdh',
                size: 'lg',
                resolve: {
                    items: () => {
                        return this.items;
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

        selected:any;

        constructor(private $modalInstance, private items) {
            this.selected = {
                item: this.items[0],
                items: [],
                remove: (item) => {
                    var index = this.selected.items.indexOf(item);
                    if (index > -1) {
                        this.selected.items.splice(index, 1);
                    }
                }

                ,
                add: (item) => {
                    function makeid() {
                        var text = '';
                        var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

                        for (var i = 0; i < 5; i++) {
                            text += possible.charAt(Math.floor(Math.random() * possible.length));
                        }
                        return text;
                    }

                    if (this.selected.items.indexOf(item) === -1) {
                        item.uniqueid = makeid();
                        this.selected.items.push(item);
                    }
                }
            };
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

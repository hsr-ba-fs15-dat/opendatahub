/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    class odhqlSelectController {

        public items:{};
        public selected:string;

        constructor(private $modal, private $log) {
            // controller init
            this.items = ['item1', 'item2', 'time3'];
        }



        public open() {
            var modalInstance = this.$modal.open({
                templateUrl: 'myModalContent.html',
                controller: 'odhqlSelectInstanceController',
                resolve: {
                    items: function () {
                        return this.items;
                    }
                }
            });

            modalInstance.result.then(function (selectedItem) {
                this.selected = selectedItem;
            }, function () {
                this.$log.info('Modal dismissed at: ' + new Date());
            });
        }


    }


    class odhqlSelectInstanceController {

        selected:any;
        constructor (private $modalInstance, private items){
            this.selected = {
                item: this.items[0]
            }
        }
        public ok(){
            this.$modalInstance.close(this.selected.item);
        }
        public cancel(){
            this.$modalInstance.dismiss('cancel');
        }
    }
    angular.module('openDataHub.main').controller('odhqlSelectController', odhqlSelectController);
    angular.module('openDataHub.main').controller('odhqlSelectInstanceController', odhqlSelectInstanceController);
}

/// <reference path='../../all.d.ts' />


module odh {
    'use strict';

    export class OdhQLController {

        public query:string;
        public columns:string[];
        public rows:{};
        public submitted:boolean = false;


        constructor(private $http:ng.IHttpService, private $state:ng.ui.IStateService, private $scope:any,
                    private ToastService:odh.utils.ToastService, private $window:ng.IWindowService, private $upload,
                    private UrlService:odh.utils.UrlService) {
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

/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    class OdhQLConsoleController {

        public query:string;
        public columns:string[];
        public rows:{};

        constructor(private $log:ng.ILogService, private $http:ng.IHttpService,
                    private UrlService:odh.utils.UrlService) {

        }

        public execute() {
            this.$http.get(this.UrlService.get('odhql'), {params: {query: this.query}}).then((data:any) => {
                this.columns = data.data.columns;
                this.rows = data.data.data;
            });
        }
    }
    angular.module('openDataHub.main').controller('OdhQLConsoleController', OdhQLConsoleController);
}

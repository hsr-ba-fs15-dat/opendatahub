/// <reference path='../../all.d.ts' />

module odh.main {
    'use strict';

    class PackageListController {

        public tableParams:any;
        public loading = true;

        constructor(private $log:ng.ILogService,
                    private PackageService:odh.main.PackageService,
                    private ToastService:odh.utils.ToastService,
                    private $auth:any, private ngTableParams,
                    private $state:ng.ui.IStateService) {
            this.tableParams = new ngTableParams({
                    page: 1,
                    count: 50,
                    limit: 50
                },
                {
                    counts: [10, 25, 50, 100],
                    total: 0,
                    getData: ($defer, params) => {
                        this.PackageService.getList(params.url()).then(result => {
                            params.total(result.count);
                            $defer.resolve(result.results);
                            this.loading = false;
                        }).catch(error => this.onError(error));
                    }
                });
        }

        public isAuthenticated() {
            return this.$auth.isAuthenticated();
        }

        public detail(row) {
            this.$state.go(row.type === 'transformation' ? 'transformation-detail' : 'document', {id: row.id});
        }

        private onError(error) {
            this.loading = false;
            this.ToastService.failure('Suche fehlgeschlagen');
            this.$log.error(error);
        }

    }


    angular.module('openDataHub.main')
        .controller('PackageListController', PackageListController);

}

/// <reference path='../../all.d.ts' />


module odh {
    'use strict';
    export class OdhQLListController {

        public tableParams:any;

        constructor(private $http:ng.IHttpService, private $state:ng.ui.IStateService, private $scope:any,
                    private ToastService:odh.utils.ToastService, private $window:ng.IWindowService, private $upload,
                    private UrlService:odh.utils.UrlService, private FileGroupService:main.FileGroupService,
                    private DocumentService:main.DocumentService,
                    private $log:ng.ILogService, private ngTableParams, public $filter:ng.IFilterService,
                    private $auth:any, private TransformationService:main.TransformationService) {

            this.tableParams = new ngTableParams({
                page: 1,            // show first page
                count: 10,           // count per page
                limit: 10
            }, {
                counts: [10, 25, 50, 100],
                total: 0, // length of data
                getData: ($defer, params) => {
                    TransformationService.getList(params.url()).then(result => {
                        params.total(result.count);
                        $defer.resolve(result.results);
                    });
                }
            });

        }

        public remove(transformation) {
            this.TransformationService.remove(transformation).then(() => {
                this.tableParams.reload();
            });


        }

    }
    angular.module('openDataHub.main').controller('OdhQLListController', OdhQLListController);

}

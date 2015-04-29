/// <reference path='../../all.d.ts' />


module odh {
    'use strict';
    export class TransformationListController {

        public tableParams:any;

        constructor(private ngTableParams, private TransformationService:main.TransformationService) {

            this.tableParams = new ngTableParams({
                    page: 1,            // show first page
                    count: 50,           // count per page
                    limit: 50
                },
                {
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
    }
    angular.module('openDataHub.main').controller('TransformationListController', TransformationListController);

}

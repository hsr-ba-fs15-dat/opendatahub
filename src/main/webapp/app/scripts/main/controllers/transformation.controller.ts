/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    class TransformationController {
        public alerts:Object[] = [];
        public columns:string[];
        public rows:{};
        public transformation:any;

        constructor(private $http:ng.IHttpService, private $state:ng.ui.IStateService, private $scope:any,
                    private ToastService:odh.utils.ToastService, private $window:ng.IWindowService, private $upload,
                    private UrlService:odh.utils.UrlService, private FileGroupService:main.FileGroupService,
                    private DocumentService:main.DocumentService,
                    private $log:ng.ILogService, private ngTableParams, public $filter:ng.IFilterService,
                    private $auth:any, private TransformationService:main.TransformationService) {
            // controller init
        }
    }
    angular.module('openDataHub.main').controller('TransformationController', TransformationController);
}

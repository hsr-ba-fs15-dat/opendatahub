/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export class PackageService {
        private packages:restangular.IElement;


        constructor(private $log:ng.ILogService, private Restangular:restangular.IService) {

            this.packages = this.Restangular.all('package');
        }

        public get(packageId:number) {
            return this.packages.get(packageId);
        }

        public getAll() {
            return this.packages.getList();
        }

        public search(query:string, mineOnly:boolean = false, page:number = 1) {
            var params:any = {page: page};
            if (query) {
                params.search = query;
            }
            if (mineOnly) {
                params.owneronly = true;
            }
            this.$log.debug('package list parameters', params);
            return this.packages.getList(params);
        }

        public getList(params:any) {
            return this.Restangular.oneUrl('package', '').get(params);
        }
    }

    angular.module('openDataHub.main')
        .service('PackageService', PackageService);
}

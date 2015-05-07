/// <reference path='../../all.d.ts' />
///<reference path="transformation.service.ts"/>


module odh.main {
    'use strict';

    export class PackageService {
        private packages:restangular.IElement;


        constructor(private $log:ng.ILogService, private Restangular:restangular.IService,
                    private $q:ng.IQService, private $http:ng.IHttpService) {

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

        public getPreview(pkg:any, params:any) {
            var promise;
            if (typeof pkg === 'object') {
                if (typeof pkg.preview === 'string') {
                    promise = this.$http.get(pkg.preview, {params: params});
                } else if (typeof pkg.url === 'string') {
                    promise = this.$http.get(pkg.url, {params: params});
                } else {
                    promise = this.$q.reject('Dieses Dokument enthält kein gültiges Preview!');
                }
                return promise;
            }
        }
    }

    angular.module('openDataHub.main')
        .service('PackageService', PackageService);
}

/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export class DocumentService {
        private documents:restangular.IElement;


        constructor(private $log:ng.ILogService, private $resource:ng.resource.IResourceService,
                    UrlService:odh.utils.UrlService, private Restangular:restangular.IService) {

            this.documents = this.Restangular.all('document');
        }

        public get(documentId:number) {
                        (<any>window).ral = this.Restangular;

            return this.documents.get(documentId);
        }

        public getAll() {
            return this.documents.getList();
        }

        public search(query:string, page:number = 1) {
            var params:any = { page: page };
            if (query) {
                params.search = query;
            }
            this.$log.debug('Document list parameters', params);
            return this.documents.getList(params);
        }
    }

    export class FileGroupService {
        constructor(private $log:ng.ILogService, private $resource:ng.resource.IResourceService,
                    UrlService:odh.utils.UrlService, private Restangular:restangular.IService) {
        }

        public getAll(documentId) {
            return this.Restangular.one('document', documentId).getList('filegroup');
        }
    }

    angular.module('openDataHub.main')
        .service('DocumentService', DocumentService)
        .service('FileGroupService', FileGroupService);
}

/// <reference path='../../all.d.ts' />


module odh {
    'use strict';

    export class DocumentService {
        private documents:restangular.IElement;


        constructor(private $log:ng.ILogService, private $resource:ng.resource.IResourceService,
                    UrlService:odh.utils.UrlService, private Restangular:restangular.IService) {

            this.documents = this.Restangular.all('documents');
        }

        public get(documentId:number) {
                        (<any>window).ral = this.Restangular;

            return this.documents.get(documentId);
        }

        public getAll() {
            return this.Restangular.all('documents');
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
    angular.module('openDataHub.main').service('documentService', DocumentService);
}

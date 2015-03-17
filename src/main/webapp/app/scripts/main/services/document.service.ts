/// <reference path='../../all.d.ts' />


module odh {
    'use strict';

    export class DocumentService {
        private documents;

        constructor(private $log:ng.ILogService, private $resource:ng.resource.IResourceService) {
            this.documents = $resource('/api/v1/documents/:id');
        }

        public get(documentId:number) {
            return this.documents.get({id: documentId}).$promise;
        }

        public search(query:string, page:number = 1) {
            var params:any = { page: page };
            if (query) {
                params.search = query;
            }
            this.$log.debug('Document list parameters', params);
            return this.documents.get(params).$promise;
        }

    }
    angular.module('openDataHub.main').service('documentService', DocumentService);
}

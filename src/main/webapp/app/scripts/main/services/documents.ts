/// <reference path='../../all.d.ts' />


module odh {
    'use strict';

    export interface IDocument extends ng.resource.IResource<Document> {
        name: string
        description: string
    }

    export class DocumentService implements ng.IServiceProvider {
        private documents;

        constructor(private $log:ng.ILogService, private $resource:ng.resource.IResourceService) {
            this.documents = $resource('http://localhost:5000/api/v1/documents');
        }

        public $get(query:string, page:number = 1) {
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

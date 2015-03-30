/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export class DocumentService {
        private documents:restangular.IElement;


        constructor(private $log:ng.ILogService, private Restangular:restangular.IService) {

            this.documents = this.Restangular.all('document');
        }

        public get(documentId:number) {
            (<any>window).ral = this.Restangular;

            return this.documents.get(documentId);
        }

        public getAll() {
            return this.documents.getList();
        }

        public search(query:string, mineOnly:boolean = false, page:number = 1) {
            var params:any = {page: page};
            if (query) {
                params.search = query;
            }
            if (mineOnly) {
                params.owneronly = true;
            }
            this.$log.debug('Document list parameters', params);
            return this.documents.getList(params);
        }
    }

    export class FileGroupService {
        constructor(private $log:ng.ILogService, private $http:ng.IHttpService,
                    private Restangular:restangular.IService) {

            (<any>Restangular).extendModel('filegroup', function (filegroup) {
                filegroup.canDownload = function (formatName) {
                    return $http.get(this.data, {params: {fmt: formatName}});
                };
                return filegroup;
            });
        }

        public getAll(documentId) {
            this.$log.debug('Fetching all filegroups of document ', documentId);
            return this.Restangular.one('document', documentId).getList('filegroup');
        }
    }

    angular.module('openDataHub.main')
        .service('DocumentService', DocumentService)
        .service('FileGroupService', FileGroupService);
}

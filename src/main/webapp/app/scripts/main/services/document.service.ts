/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export class DocumentService {
        private documents:restangular.IElement;


        constructor(private $log:ng.ILogService, private Restangular:restangular.IService) {

            this.documents = this.Restangular.all('document');
        }

        public get(documentId:number) {
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

        public getList(params:any) {
            return this.Restangular.oneUrl('document', '').get(params);
        }

        public remove(transformation) {
            return this.Restangular.one('document', transformation.id).remove();
        }
    }

    export class FileGroupService {
        constructor(private $log:ng.ILogService, private $http:ng.IHttpService,
                    private Restangular:restangular.IService, private $q:ng.IQService) {

            (<any>Restangular).extendModel('filegroup', function (filegroup) {
                filegroup.canDownload = function (formatName) {
                    return $http.get(this.data, {params: {fmt: formatName}});
                };
                return filegroup;
            });
        }

        public getAll(documentId:any = false, withPreview = false, count = 3) {
            var promise:ng.IPromise<any>;
            if (!documentId) {
                this.$log.debug('Fetching all filegroups');
                promise = this.Restangular.all('fileGroup').getList();
            } else {

                this.$log.debug('Fetching all filegroups of document ', documentId);
                promise = this.Restangular.one('document', documentId).getList('filegroup');
            }

            if (withPreview) {
                var deferred = this.$q.defer();
                count = count < 3 ? 3 : count;
                promise.then((data) => {
                    var promises = [];
                    angular.forEach(data, (fg, i) => {
                        var d = this.$q.defer();
                        promises.push(d.promise);

                        this.$http({
                            url: fg.preview,
                            method: 'GET',
                            params: {
                                count: count
                            }
                        })
                            .then(data => {
                                fg.previewUrl = fg.preview;
                                fg.preview = data.data;
                                fg.preview.count = count;
                                d.resolve(data);
                            })
                            .catch((e) => d.reject(e));
                    });
                    this.$q.all(promises).then(() => {
                        deferred.resolve(data);
                    });

                });

                promise = deferred.promise;
            }

            return promise;
        }

    }

    angular.module('openDataHub.main')
        .service('DocumentService', DocumentService)
        .service('FileGroupService', FileGroupService);
}

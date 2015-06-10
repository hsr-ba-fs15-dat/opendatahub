/// <reference path='../../all.d.ts' />
///<reference path="transformation.service.ts"/>


module odh.main {
    'use strict';
    /**
     * represents the Packages (Transformations AND Documents)
     *
     */
    export class PackageService {
        public transformationPrefix:string;
        public packagePrefix:string;
        private packages:restangular.IElement;

        constructor(private $log:ng.ILogService, private Restangular:restangular.IService,
                    private $q:ng.IQService, private $http:ng.IHttpService, private AppConfig:odh.IAppConfig,
                    private $window:ng.IWindowService, private ToastService:odh.utils.ToastService) {

            this.packages = this.Restangular.all('package');
            this.AppConfig.then(config => {
                this.transformationPrefix = config.TRANSFORMATION_PREFIX;
                this.packagePrefix = config.PACKAGE_PREFIX;
            });
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


        public download(filegroup, format) {
            return this.Restangular.oneUrl(filegroup.route, filegroup.token).get({fmt: format}).then(res => {
                filegroup.canDownload(format).then(() => {
                    this.$window.location.href = filegroup.data +
                    ( format ? '?fmt=' + format : '') + '&token=' + res.token;
                }).catch(() => {
                    this.ToastService.failure('Die Datei konnte nicht ins gewünschte Format konvertiert werden.');
                });
            });
        }

        public getPreviewByUniqueName(uniquename:string, params) {
            var packagePrefix = this.packagePrefix || 'ODH';
            var transformationPrefix = this.transformationPrefix || 'TRF';
            if (!this.packagePrefix) {
                console.warn('AppConfig not loaded successfully. Falling back to default!');
            }
            var regex = '^({0}|{1})(\\d+)_?(.*)$'.format(packagePrefix, transformationPrefix);
            var re = new RegExp(regex);
            var result = re.exec(uniquename);
            var defer = this.$q.defer();
            var pkg;
            if (result) {
                if (result[1] === packagePrefix) {
                    pkg = 'document';
                }
                if (result[1] === transformationPrefix) {
                    pkg = 'transformation';
                }
                this.Restangular.one(pkg, result[2]).one('preview').get(params).then(data => {
                    angular.forEach(data, (each, key) => {
                        if (each.name === result[3]) {
                            defer.resolve(data[key]);
                        }
                    });

                });
                return defer.promise;
            }
            return null;

        }

        public getPreview(pkg:any, params:any) {
            var promise;
            var defer = this.$q.defer();
            var fromPreviewUrl = (preview) => {
                return this.$http.get(preview, {params: params});
            };
            if (typeof pkg === 'object') {
                if (pkg.type === 'preview') {
                    this.$log.debug('Got a Preview. Fetching new one!');
                    if (isUrl(pkg.preview)) {
                        this.$log.debug('preview field is a URL. Will fetch it from there!');
                        fromPreviewUrl(pkg.preview).then(result => {
                            if (result) {
                                defer.resolve(result);
                            }
                        });
                    } else if (isUrl(pkg.url)) {
                        this.$log.debug('There is a URL Field. Will fetch it from there!');
                        fromPreviewUrl(pkg.url).then(result => {
                            if (result) {
                                defer.resolve(result.data[0]);
                            }
                        }).catch(console.error);
                    } else if (typeof pkg.unique_name === 'string') {
                        this.$log.debug('There is a Unique Name ({0}). Fetching preview with this one'
                            .format(pkg.unique_name));
                        return this.getPreviewByUniqueName(pkg.unique_name, params);
                    } else {
                        console.error('Could not fetch the Preview. Here is the Package:', pkg);
                    }


                }
                if (pkg.type === 'transformation') {
                    if (!pkg.is_template) {
                        this.$log.debug('Got a Transformation. Fetching a Preview of it!');
                        if (isUrl(pkg.preview)) {
                            fromPreviewUrl(pkg.preview).then(result => {
                                defer.resolve(result.data[0]);
                            });
                        } else {
                            defer.reject({
                                data: {
                                    type: 'error',
                                    error: 'Fehler beim laden des Previews. Fehlerhafte Serverabfrage'
                                }
                            });
                        }
                    }
                    if (pkg.is_template) {
                        this.$log.debug('Got a Transformation. But it\'s a Template. Done nothing!');
                        defer.reject({
                            data: {
                                type: 'info',
                                error: 'Es kann keine Vorschau eines Templates erstellt werden'
                            }
                        });
                    }


                }
                if (pkg.type === 'document') {
                    this.$log.debug('Got a document. Fetching a Preview of it!');
                    if (isUrl(pkg.preview)) {
                        fromPreviewUrl(pkg.preview).then(result => {
                            defer.resolve(result);
                        });
                    }
                }
                return defer.promise;
            }


            function isUrl(s) {
                var regexp = /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
                return regexp.test(s);
            }

            return promise;
        }
    }

    angular.module('openDataHub.main')
        .service('PackageService', PackageService);
}

/// <reference path='../all.d.ts' />


module odh {
    'use strict';


    export interface IAppConfig extends ng.IPromise<any> {

    };

    class AppConfigProvider {

        public deferred:ng.IDeferred<any>;

        /* @ngInject */
        public $get($http:ng.IHttpService, $q:ng.IQService, UrlService:odh.utils.UrlService):IAppConfig {
            this.deferred = $q.defer();
            var appConfig:any = {};

            $http.get(UrlService.get('config')).success((data:any) => {
                angular.extend(appConfig, data);
                this.deferred.resolve(appConfig);
            }).catch((res) => {
                this.deferred.reject(res);
            });

            return this.deferred.promise;
        }
    }
    angular.module('openDataHub').provider('AppConfig', AppConfigProvider);
}

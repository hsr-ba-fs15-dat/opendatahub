/// <reference path='../all.d.ts' />


module odh.utils {
    'use strict';

    export class UrlService {

        private apiPrefix:string = '';
        private $interpolate:ng.IInterpolateService;

        /* @ngInject */
        public $get($interpolate:ng.IInterpolateService) {
            this.$interpolate = $interpolate;
            return this;
        }

        public setApiPrefix(prefix:string) {
            this.apiPrefix = prefix;
        }

        public get(url:string, replace:any = {}):string {
            url = this.$interpolate(this.apiPrefix + url)(replace);
            url += url.substring(url.length - 1) === '/' ? '' : '/';
            return url;
        }

    }
    angular.module('openDataHub.utils').provider('UrlService', UrlService);
}

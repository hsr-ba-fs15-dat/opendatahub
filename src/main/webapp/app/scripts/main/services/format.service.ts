/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export interface IFormat {
        label:string;
        description:string;
        example:string;
    }

    export class FormatService {

        constructor(private $http:ng.IHttpService, private UrlService:odh.utils.UrlService) {

        }

        public getAvailableFormats():ng.IHttpPromise<IFormat[]> {
            var url = this.UrlService.get('format');
            return this.$http.get<IFormat[]>(url);
        }
    }
    angular.module('openDataHub.main').service('FormatService', FormatService);
}

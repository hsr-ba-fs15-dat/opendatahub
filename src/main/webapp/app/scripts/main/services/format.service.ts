/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export interface IFormat {
        name:string;
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

        public sortByLabel(data:IFormat[]) {
            return data.sort((a, b) => { return a.label < b.label ? -1 : a.label === b.label ? 0 : 1; });
        }
    }
    angular.module('openDataHub.main').service('FormatService', FormatService);
}

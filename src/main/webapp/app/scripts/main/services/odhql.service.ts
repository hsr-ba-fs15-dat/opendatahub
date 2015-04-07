/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export class OdhQLService {

        public temp:{};

        constructor(private $http:ng.IHttpService) {

        }

        public myExposedMethod(query:string):ng.IHttpPromise<any> {
            return this.$http.post('/api/v1/method', {query: query});
        }

    }
    angular.module('openDataHub.main').service('OdhQLService', OdhQLService);
}

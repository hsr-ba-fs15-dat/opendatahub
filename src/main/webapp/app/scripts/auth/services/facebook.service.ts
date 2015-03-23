/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    export class FaceBookService {

        public temp:{};
        public loaded:boolean;

        constructor(private $q:ng.IQService, private $window:ng.IWindowService, private $rootScope:ng.IRootScopeService,
                    private ezfb) {
            this.loaded = false;
        }


        public login() {
            return this.ezfb.login(null, {scope: 'email,user_likes'});
        }


}
angular.module('openDataHub.auth').service('FaceBookService', FaceBookService);
}

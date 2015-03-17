/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    export class FaceBookService {

        public temp:{};
        public loaded: boolean;
        constructor(private $q:ng.IQService, private $window:ng.IWindowService, private $rootScope:ng.IRootScopeService,
                    private efzb) {
            this.loaded = false;
        }



        public login():ng.IPromise<any> {
            var deferred = this.$q.defer();
            // first check if we already have logged in
            this.efzb.getLoginStatus(function (response) {
                if (response.status === 'connected') {
                    // the user is logged in and has authenticated your
                    // app
                    console.log('fb user already logged in');
                    deferred.resolve(response);
                } else {
                    // the user is logged in to Facebook,
                    // but has not authenticated your app
                    this.efzb.login((response) => {
                        if (response.authResponse) {
                            console.log('fb user logged in');
                            this.resolve(null, response, deferred);
                        } else {
                            console.log('fb user could not log in');
                            this.resolve(response.error, null, deferred);
                        }
                    });
                }
            });

            return deferred.promise;
        }

        public resolve(errval, retval, deferred) {
            this.$rootScope.$apply(function () {
                if (errval) {
                    deferred.reject(errval);
                } else {
                    retval.connected = true;
                    deferred.resolve(retval);
                }
            });
        }

    }
    angular.module('openDataHub.auth').service('FaceBookService', FaceBookService);
}

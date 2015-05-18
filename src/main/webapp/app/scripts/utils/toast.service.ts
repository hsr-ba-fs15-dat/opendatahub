/// <reference path='../all.d.ts' />


module odh.utils {
    'use strict';

    export class ToastService {

        constructor(private ngToast) {

        }

        public success(msg:string):void {
            this.ngToast.create({className: 'success shadow-z-3', content: msg});
        }

        public failure(msg:string):void {
            this.ngToast.create({className: 'danger shadow-z-3', content: msg});
        }

        public warning(msg:string):void {
            this.ngToast.create({className: 'warning shadow-z-3', content: msg});
        }

    }
    angular.module('openDataHub.utils').service('ToastService', ToastService);
}

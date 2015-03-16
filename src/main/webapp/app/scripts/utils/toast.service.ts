/// <reference path='../all.d.ts' />


module odh.utils {
    'use strict';

    export class ToastService {

        public temp:{};

        constructor(private ngToast) {

        }

        public success(msg:string):void {
            this.ngToast.create({className: 'success', content: msg});
        }

        public failure(msg:string):void {
            this.ngToast.create({className: 'danger', content: msg});
        }

    }
    angular.module('openDataHub.utils').service('ToastService', ToastService);
}

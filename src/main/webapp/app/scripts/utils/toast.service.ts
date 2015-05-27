/// <reference path='../all.d.ts' />


module odh.utils {
    'use strict';
    /**
     * displays messages to the user and hides them after a short period of time
     *
     */
    export class ToastService {

        constructor(private ngToast) {

        }

        /**
         * shows a success (green)
         * @param msg
         */
        public success(msg:string):void {
            this.ngToast.create({className: 'success shadow-z-3', content: msg});
        }

        /**
         * shows a failure (red)
         * @param msg
         */
        public failure(msg:string):void {
            this.ngToast.create({className: 'danger shadow-z-3', content: msg});
        }

        /**
         * shows a warning (amber)
         * @param msg
         */
        public warning(msg:string):void {
            this.ngToast.create({className: 'warning shadow-z-3', content: msg});
        }

    }
    angular.module('openDataHub.utils').service('ToastService', ToastService);
}

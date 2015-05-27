/// <reference path='../all.d.ts' />


module odh.utils {
    'use strict';

    /**
     * Intercepts HTTP-Requests for errors and displays a warning in the GUI
     */
    export class WarningHttpInterceptor {

        constructor(private $q:ng.IQService, private ToastService:odh.utils.ToastService) {

        }

        public response = (response) => {
            if (angular.isObject(response.data) && response.data._warnings) {
                angular.forEach(response.data._warnings, (warning) => {
                    this.ToastService.warning(warning);
                });
                response.data = response.data._data;
            }
            return response;
        };

        public responseError = (rejection) => {
            return this.$q.reject(rejection);
        };

    }
    angular.module('openDataHub.utils').service('WarningHttpInterceptor', WarningHttpInterceptor);
}

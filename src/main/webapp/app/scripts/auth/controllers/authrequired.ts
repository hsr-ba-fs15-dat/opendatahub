/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';
    class AuthRequiredController {
        public awesomeThings: any;

        public email:string;
        public password:string;

        constructor() {
            this.awesomeThings = [
                'HTML5 Boilerplate',
                'AngularJS',
                'Karma'
            ];
        }


    }

    angular.module('openDataHub.auth').controller('AuthRequiredController', AuthRequiredController);
}

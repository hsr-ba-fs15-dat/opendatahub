/// <reference path='../all.d.ts' />


module odh.utils {
    'use strict';
    /**
     * is responsible for loading the application
     */
    export class AppLoader {

        public isLoaded:boolean = false;
        private pending:number = 0;

        public acquire():void {
            this.pending++;
            this.isLoaded = this.pending <= 0;
        }

        public release():void {
            this.pending--;
            this.isLoaded = this.pending <= 0;
        }

    }
    angular.module('openDataHub.utils').service('AppLoader', AppLoader);
}

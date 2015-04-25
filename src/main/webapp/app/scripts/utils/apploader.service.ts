/// <reference path='../all.d.ts' />


module odh.utils {
    'use strict';

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

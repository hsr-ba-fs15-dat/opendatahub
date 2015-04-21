/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';
    export interface ITransformation {
        name: string;
        description: string;
        transformation: string;
        'private': boolean;
        file_groups: any;
    }
    export class TransformationService {

        private transformations:restangular.IElement;


        constructor(private $log:ng.ILogService, private Restangular:restangular.IService) {

            this.transformations = this.Restangular.all('transformation');
        }

        public remove(transformation) {
            return this.Restangular.one('transformation', transformation.id).remove();
        }

        public post(transformation:ITransformation) {
            return this.transformations.post(transformation);
        }

        public get(transformationId:number) {
            (<any>window).ral = this.Restangular;

            return this.transformations.get(transformationId);
        }

        public getAll() {
            return this.transformations.getList();
        }

        public search(query:string, mineOnly:boolean = false, page:number = 1) {
            var params:any = {page: page};
            if (query) {
                params.search = query;
            }
            if (mineOnly) {
                params.owneronly = true;
            }
            this.$log.debug('Document list parameters', params);
            return this.transformations.getList(params);
        }

        public getList(params:any) {
            return this.Restangular.oneUrl('transformation', '').get(params);
        }

    }
    angular.module('openDataHub.main').service('TransformationService', TransformationService);
}

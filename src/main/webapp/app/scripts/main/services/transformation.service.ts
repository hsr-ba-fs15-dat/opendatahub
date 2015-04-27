/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';
    export     interface IField {
        name: string;
        alias: string;
    }
    export interface ITransformation {
        name: string;
        description: string;
        transformation: string;
        'private': boolean;
        file_groups: any;
    }
    export interface IFileGroup {

    }
    export interface ITable {
        uniqueId: string;
        parent: string;
        name: string;
        uniqueIdAlias: string;
        'private': boolean;
        types: any[];
        cols: any[];
        count: number;
    }
    export interface IExpression {
        foreignKey?: IField;
        joinField?: IField;
        joinTable?: any;
        operation: IOperation;
    }
    export interface IOperation {
        label: string;
        operation:string;
    }

    export interface IOperations {
        join: IOperation;
        none: IOperation;
        union: IOperation;
    }
    export interface ITransformationSelection {
        fileGroups: IFileGroup[];
        items: ITable[];
        fields: {};
        expression: {[name:string]: IExpression};
        unionTargets: ITable[];
        joinTargets: ITable[];
        master: string;
        removeTable (item:ITable):void;
        addTable (item:ITable):void;
        addRemoveField(col:any, table:main.ITable):void;
        generateTransformation():string;
        toggleQuotes():void;
        addRemoveTable(item:main.ITable):void;
        getTableByName(tableName:string):main.ITable;
        tableSelected(table:main.ITable):boolean;
        allTables():ITable[];
        getFields(tableName:string):main.IField[];
        getJoinOperation(table:main.ITable);
        getSelectedFields(table:main.ITable):main.IField[];
        isPrivate():boolean;
        getFileGroups():main.IFileGroup[];
    }
    export class TransformationService {

        private transformations:restangular.IElement;


        constructor(private $log:ng.ILogService, private Restangular:restangular.IService,
                    private $http:ng.IHttpService,
                    private UrlService:odh.utils.UrlService) {

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

        public preview(transformation:string) {
            return this.$http.get(this.UrlService.get('odhql'), {
                params: {
                    query: transformation
                }
            });


        }

        public parse(transformation:string) {
            return this.$http.get(this.UrlService.get('parse'), {
                params: {
                    query: transformation
                }
            });
        }

    }
    angular.module('openDataHub.main').service('TransformationService', TransformationService);
}

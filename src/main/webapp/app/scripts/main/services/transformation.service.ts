/// <reference path='../../all.d.ts' />

/**
 * @module odh.main
 */
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
    }

    export interface IFileGroup {

    }

    export interface ITable {
        uniqueId: string;
        unique_name: string;
        parent: string;
        name: string;
        uniqueIdAlias: string;
        ngTableParams: any;
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
        joinTargets: ITable[];
        master: string;
        removeTable (item:ITable):void;
        addTable (item:ITable):void;
        addRemoveField(col:any, table:main.ITable):void;
        addField(col:any, table:main.ITable):void;
        generateTransformation():string;
        setQuotes(value:boolean):void;
        getQuotes():boolean;
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

        public name;
        public description;
        public transformation;
        public forceManualEdit;
        private transformations:restangular.IElement;

        constructor(private $log:ng.ILogService, private Restangular:restangular.IService,
                    private $http:ng.IHttpService,
                    private UrlService:odh.utils.UrlService, private $q:ng.IQService) {
            (<any>Restangular).extendModel('transformation', function (transformation) {
                transformation.canDownload = function (formatName) {
                    return $http.get(this.data, {params: {fmt: formatName}});
                };
                return transformation;
            });
            this.transformations = this.Restangular.all('transformation');

        }

        public static aceLoaded(editor) {
            editor.$blockScrolling = 'Infinity';
            var _renderer = editor.renderer;
            var _session = editor.getSession();
            _session.setOptions({mode: 'ace/mode/sql'});
            _renderer.setOptions({
                maxLines: Infinity
            });
            editor.setOptions({
                showGutter: true,
                firstLineNumber: 1
            });
        }

        public remove(transformation) {
            return this.Restangular.one('transformation', transformation.id).remove();
        }

        public post(transformation:ITransformation) {
            return this.transformations.post(transformation);
        }

        public get(transformationId:number) {
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

        public preview(transformation:any, params = null) {
            var deferred = this.$q.defer();
            if (typeof transformation === 'object') {
                if (transformation.type === 'transformation') {
                    this.Restangular.one('transformation', transformation.id).one('preview').get(params)
                        .then((data => {
                            deferred.resolve(data);
                        }));

                }
            }
            if (typeof transformation === 'string') {
                this.$http.post(this.UrlService.get('transformation/adhoc'), {
                    params: {
                        query: transformation

                    }
                }, {params: params}).then(data => {
                    deferred.resolve(data.data[0]);
                }).catch(data => {
                    deferred.reject(data);
                });
            }

            return deferred.promise;
        }

        public parse(transformation:string) {
            if (transformation && transformation !== '') {
                return this.$http.post(this.UrlService.get('parse'), {
                    params: {
                        query: transformation
                    }
                });
            } else {
                return this.$q.reject('No Transformation given! This should not happen!');
            }

        }

    }
    angular.module('openDataHub.main').service('TransformationService', TransformationService);
}

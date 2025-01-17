/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';
    /**
     * the connection between two tables
     */
    export interface IExpression {
        foreignKey?: IField;
        joinField?: IField;
        joinTable?: any;
        operation: IOperation;
    }

    /**
     * the connection between two tables
     */
    export interface IOperation {
        label: string;
        operation:string;
    }

    /**
     * the possible connections between two tables
     */
    export interface IOperations {
        join: IOperation;
        none: IOperation;
        union: IOperation;
    }

    /**
     *  interfaces the logic behind the assistant.
     */
    export interface ITransformationSelection {
        fileGroups: main.IFileGroup[];
        items: ITable[];
        fields: {};
        expression: {[name:string]: IExpression};
        joinTargets: ITable[];
        master: string;
        init ():void;
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

    /**
     * Represents a to be created transformation.
     * Contains the Assistants logic
     * - provides table addition/removal
     * - provides field addition/removal
     * - provides field-name generation
     * - provides table-alias generation
     * - checks if tables are odh values
     * - automatically quotes field names
     */
    export class TransformationSelection implements main.ITransformationSelection {

        public fileGroups:main.IFileGroup[];
        public items:main.ITable[];
        public fields:{};
        public expression:{[name:string]: IExpression} = {};
        public joinTargets:main.ITable[];
        public master:string;
        private useQuotes:boolean = false;
        private privateCount:number = 0;
        private itemCounter:number = 1;

        constructor(private JOIN_OPERATIONS:main.IOperations, private ngTableParams:any,
                    private PackageService:main.PackageService) {
            this.init();

        }
        /* @ngInject */
        public $get() {
            return this;
        }

        public init() {
            this.items = [];
            this.expression = {};
            this.fields = {};
            this.joinTargets = [];
            this.fileGroups = [];
        }

        public addTable(item:main.ITable) {
            if (this.items.indexOf(item) === -1) {
                item.uniqueIdAlias = 't' + this.itemCounter++;
                item.ngTableParams = new this.ngTableParams({
                        page: 1,            // show first page
                        count: 3           // count per page
                    },
                    {
                        counts: [3, 10, 25, 100],
                        total: 0, // length of data
                        getData: ($defer, params) => {
                            this.PackageService.getPreview(item, params.url()).then(result => {
                                params.total(result.count);
                                $defer.resolve(result.data);

                            }).catch(err => console.error(err));
                        }
                    });
                this.expression[item.unique_name] = {operation: this.JOIN_OPERATIONS.none};
                this.items.push(item);
                this.fields[item.unique_name] = [];
                this.fileGroups.push(item.parent);
                if (item.private) {
                    this.privateCount += 1;
                }
            }
        }

        public removeTable(item:main.ITable) {
            var index = this.items.indexOf(item);
            if (index > -1) {
                this.items.splice(index, 1);
            }
            delete this.fields[item.unique_name];
            delete this.expression[item.unique_name];
            if (item.private) {
                this.privateCount -= 1;
            }
            this.fileGroups.splice(this.fileGroups.indexOf(item.parent), 1);
        }

        public allTables() {
            return this.items;
        }

        public getFields(tableName:string) {
            return this.fields[tableName];
        }

        public addRemoveTable(item:main.ITable) {
            var index = this.items.indexOf(item);
            if (index === -1) {
                this.addTable(item);
            } else {
                this.removeTable(item);
            }
        }

        public getTableByName(tableName:string) {
            for (var i = 0; i < this.items.length; i++) {
                if (this.items[i].unique_name === tableName) {
                    return this.items[i];
                }
            }
        }

        public isPrivate() {
            return !(this.privateCount === 0);
        }

        public getSelectedFields(table:main.ITable) {
            return this.fields[table.unique_name];
        }

        /**
         * Checks if the Table is selected.
         * @returns boolean
         */
        public tableSelected(table) {

            return this.items.indexOf(table) > -1;
        }

        public generateTransformation() {
            var fields:string[] = [];
            var master:main.ITable;
            var joinStatements:string[];
            var unionStatements:string[];
            unionStatements = [];
            joinStatements = [];
            this.joinTargets = [];
            angular.forEach(this.expression, (value:IExpression, key:string) => {
                var table = this.getTableByName(key);
                if (!value.operation.operation || value.operation.operation === 'none') {
                    if (!master) {
                        fields = this.createFieldNames(this.fields[key], table.uniqueIdAlias).concat(fields);
                        master = table;
                        this.joinTargets.push(table);

                    }

                }
                if (value.operation.operation === 'union') {
                    this.joinTargets.push(table);
                    var unionFields = this.createFieldNames(this.fields[key], table.uniqueIdAlias);
                    unionStatements.push(' \nUNION \n SELECT '.concat(unionFields.join(',\n'),
                        ' FROM ', this.aliasedTable(table)));
                }
                if (value.operation.operation === 'join') {
                    this.joinTargets.push(table);

                    if (value.foreignKey) {
                        fields = this.createFieldNames(this.fields[key], table.uniqueIdAlias).concat(fields);
                        joinStatements.push(
                            ' JOIN '.concat(
                                this.aliasedTable(table),
                                ' on ',
                                this.createFieldNames([value.foreignKey], value.joinTable.uniqueIdAlias, true)[0],
                                ' = ',
                                this.createFieldNames([value.joinField], table.uniqueIdAlias, true)[0]
                            )
                        );
                    }


                }

            });
            if (master && fields) {
                return 'SELECT '.concat(
                    fields.join(',\n'),
                    ' \nFROM ',
                    this.aliasedTable(master),
                    ' \n',
                    joinStatements.join(' \n '),
                    unionStatements.join(' \n')
                );
            }
        }

        public setQuotes(value:boolean) {
            this.useQuotes = value;
            this.generateTransformation();
        }

        public getQuotes():boolean {
            return this.useQuotes;
        }

        public addRemoveField(col, table:main.ITable) {
            this.fields[table.unique_name] = this.fields[table.unique_name] || [];
            var index = this.fields[table.unique_name].indexOf(col);
            if (index > -1) {
                this.fields[table.unique_name].splice(index, 1);
            } else {
                this.fields[table.unique_name].push(col);
            }
        }


        public addField(col, table:main.ITable) {
            this.fields[table.unique_name] = this.fields[table.unique_name] || [];
            var index = this.fields[table.unique_name].indexOf(col);
            if (index === -1) {
                this.fields[table.unique_name].push(col);
            }
        }

        public getFileGroups() {
            return this.fileGroups;
        }

        public getJoinOperation(table:main.ITable) {
            return this.expression[table.unique_name].operation;
        }

        private aliasedTable(table:ITable):string {
            if (table.unique_name === table.uniqueIdAlias) {
                return this.quote(table.unique_name);
            } else {
                return [this.quote(table.unique_name), this.quote(table.uniqueIdAlias)].join(' as ');
            }
        }

        private createFieldNames(fields:IField[], group:string, doNotCheckAlias:boolean = false):string[] {
            var newFields = [];
            angular.forEach(fields, (field) => {
                newFields.push(
                    [this.quote(group), (field.name === field.alias || doNotCheckAlias)
                        ? this.quote(field.name) : [this.quote(field.name), this.quote(field.alias)].join(' AS ')]
                        .join('.'));
            });
            return newFields;
        }

        private quote(field:string) {
            var regEx = new RegExp('^[a-zA-Z_][a-zA-Z0-9_]*$');
            if (this.useQuotes || !regEx.test(field)) {

                return '"' + field + '"';
            }
            return field;
        }


    }

    var joinOperations = {

        none: {
            label: 'Nein',
            operation: null
        },
        union: {
            label: 'per UNION',
            operation: 'union'
        },
        join: {
            label: 'per JOIN',
            operation: 'join'
        }
    };

    angular.module('openDataHub.main').service('TransformationSelection', TransformationSelection);
    angular.module('openDataHub.main').constant('JOIN_OPERATIONS', joinOperations);
}

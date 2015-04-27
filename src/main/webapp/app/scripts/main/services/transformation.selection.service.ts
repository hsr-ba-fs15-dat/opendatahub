/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';

    export class TransformationSelection implements main.ITransformationSelection {

        public fileGroups:main.IFileGroup[];
        public items:main.ITable[];
        public fields:{};
        public expression:{[name:string]: IExpression} = {};
        public unionTargets:main.ITable[];
        public joinTargets:main.ITable[];
        public master:string;
        public joinOperations:any;
        private useQuotes:boolean = true;
        private privateCount:number = 0;

        constructor(private JOIN_OPERATIONS:main.IOperations) {
            this.items = [];
            this.expression = {};
            this.fields = {};
            this.joinTargets = [];
            this.fileGroups = [];
        }

        public $get() {
            return this;
        }

        public addTable(item:main.ITable) {
            if (this.items.indexOf(item) === -1) {
                item.uniqueId = item.name;
                item.uniqueIdAlias = item.name;
                this.expression[item.uniqueId] = {operation: this.JOIN_OPERATIONS.none};
                this.items.push(item);
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
            delete this.fields[item.uniqueId];
            delete this.expression[item.uniqueId];
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
                if (this.items[i].uniqueId === tableName) {
                    return this.items[i];
                }
            }
        }

        public isPrivate() {
            return !(this.privateCount === 0);
        }

        public getSelectedFields(table:main.ITable) {
            return this.fields[table.uniqueId];
        }

        public tableSelected(table) {
            /**
             * Checks if the Table is selected.
             * @returns boolean
             */
            return this.items.indexOf(table) > -1;
        }

        public generateTransformation() {
            var fields:string[] = [];
            var master:string = '';
            var joinStatements:string[];
            var unionStatements:string[];
            unionStatements = [];
            joinStatements = [];

            this.joinTargets = [];

            angular.forEach(this.expression, (value:IExpression, key:string) => {

                if (!value.operation.operation || value.operation.operation === 'none') {
                    if (!master) {
                        fields = this.createFieldNames(this.fields[key], key).concat(fields);
                        master = key;
                        this.joinTargets.push(this.getTableByName(key));

                    }

                }
                if (value.operation.operation === 'union') {
                    this.joinTargets.push(this.getTableByName(key));
                    var unionFields = this.createFieldNames(this.fields[key], key);
                    unionStatements.push(' \nUNION \n SELECT '.concat(unionFields.join(',\n'),
                        ' FROM "', key + '"'));
                }
                if (value.operation.operation === 'join') {
                    this.joinTargets.push(this.getTableByName(key));

                    if (value.foreignKey) {
                        fields = this.createFieldNames(this.fields[key], key).concat(fields);
                        joinStatements.push(
                            ' JOIN '.concat(
                                this.quote(key),
                                ' on ',
                                this.createFieldNames([value.foreignKey], value.joinTable.uniqueId, true)[0],
                                ' = ',
                                this.createFieldNames([value.joinField], key, true)[0]
                            )
                        );
                    }


                }

            });
            if (master && fields) {
                return 'SELECT '.concat(
                    fields.join(',\n'),
                    ' \nFROM ',
                    this.quote(master),
                    ' \n',
                    joinStatements.join(' \n '),
                    unionStatements.join(' \n')
                );
            }
        }

        public toggleQuotes() {
            this.useQuotes = !this.useQuotes;
        }

        public addRemoveField(col, table:main.ITable) {
            this.fields[table.uniqueId] = this.fields[table.uniqueId] || [];
            var index = this.fields[table.uniqueId].indexOf(col);
            if (index > -1) {
                this.fields[table.uniqueId].splice(index, 1);
            } else {
                this.fields[table.uniqueId].push(col);
            }
        }

        public getFileGroups() {
            return this.fileGroups;
        }

        public getJoinOperation(table:main.ITable) {
            return this.expression[table.uniqueId].operation;
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

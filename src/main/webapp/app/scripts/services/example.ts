/// <reference path='../all.d.ts' />
'use strict';

/**
 * @ngdoc service
 * @name opendatahubApp.example
 * @description
 * # test
 * Service in the opendatahubApp.
 */
class ExampleService {

    constructor(private $log: ng.ILogService) {
        $log.info('ExampleService here')
    }
}

app.service('ExampleService', ExampleService);


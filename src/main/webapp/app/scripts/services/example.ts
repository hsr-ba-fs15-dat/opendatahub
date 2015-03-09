/// <reference path='../../../typings/tsd.d.ts' />
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

angular.module('opendatahubApp').service('ExampleService', ExampleService);

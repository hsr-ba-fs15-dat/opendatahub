/// <reference path='../all.d.ts' />
/**
 * Container Module for the OpenDataHub Application
 * Contains the submodules and some basic logic
 */
module odh {
    'use strict';

    angular
        .module('openDataHub.main', [
            'angularFileUpload'
        ]);
}

/// <reference path='../../../typings/tsd.d.ts' />
module openDataHub.Authentication {
    'use strict';

    angular
        .module('openDataHub.auth', [
            'openDataHub.auth.controllers',
            'openDataHub.auth.services'
        ]);

    angular
        .module('openDataHub.auth.controllers', []);

    angular
        .module('openDataHub.auth.services', ['ngCookies']);
}
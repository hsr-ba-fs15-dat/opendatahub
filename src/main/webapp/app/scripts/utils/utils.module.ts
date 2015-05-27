/// <reference path='../all.d.ts' />
/**
 * contains some helper classes and functions for the OpenDataHub Application.
 */
module odh.utils {
    'use strict';

    angular
        .module('openDataHub.utils', [
            'ngToast',
            'ngAnimate'
        ])

        .config((ngToastProvider) => {

            ngToastProvider.configure({
                horizontalPosition: 'center',
                verticalPosition: 'top',
                animation: 'slide'
            });

        });
}

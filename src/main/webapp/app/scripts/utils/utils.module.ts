/// <reference path='../all.d.ts' />

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

/// <reference path='../all.d.ts' />


module odh.utils {
    'use strict';

    function odhBlock():ng.IDirective {
        return {
            restrict: 'A',
            link: (scope:ng.IScope, element:any, attrs:any) => {
                var expr = attrs.odhBlock;
                var text = attrs.odhBlockText ? '&nbsp;<span style="font-size: 2.5em;">' + attrs.odhBlockText +
                    '</span>' : '';

                var icon = '<svg class="spinner" width="65px" height="65px" viewBox="0 0 66 66"' +
                        'xmlns="http://www.w3.org/2000/svg"><circle class="path" fill="none" stroke-width="6" ' +
                        'stroke-linecap="round" cx="33" cy="33" r="30"></circle> </svg>';

                scope.$watch(expr, function (newVal, oldVal) {
                    if (newVal) {
                        element.block({
                            message: icon + text,
                            css: {
                                border: 'none',
                                padding: '15px',
                                // backgroundColor: '#000',
                                backgroundColor: 'none', // swap these for border/box
                                '-webkit-border-radius': '10px',
                                '-moz-border-radius': '10px',
                                '-ms-border-radius': '10px',
                                'border-radius': '10px',
                                opacity: 0.5,
                                color: '#fff'
                            }
                        });
                    } else {
                        element.unblock();
                    }
                });
            }
        };
    }

    angular.module('openDataHub').directive('odhBlock', odhBlock);
}

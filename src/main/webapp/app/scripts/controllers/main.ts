/// <reference path='../../../typings/tsd.d.ts' />
'use strict';


class MainCtrl {

    constructor(private $scope) {
        console.log(this.$scope)
    }

}

angular.module('opendatahubApp').controller('MainCtrl', MainCtrl);

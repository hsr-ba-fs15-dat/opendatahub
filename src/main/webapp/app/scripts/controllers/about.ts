/// <reference path='../../../typings/tsd.d.ts' />
'use strict';


class AboutCtrl {

    constructor(private $scope) {
        console.log(this.$scope)
    }

}

angular.module('opendatahubApp').controller('AboutCtrl', AboutCtrl);

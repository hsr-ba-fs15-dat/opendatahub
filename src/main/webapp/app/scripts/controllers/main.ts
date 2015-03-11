/// <reference path='../all.d.ts' />
'use strict';


class MainCtrl {

    constructor(private $scope) {
        console.log(this.$scope)
    }

}

angular.module('openDataHub').controller('MainCtrl', MainCtrl);

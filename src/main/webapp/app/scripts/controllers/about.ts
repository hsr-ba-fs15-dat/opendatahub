/// <reference path='../all.d.ts' />
'use strict';


class AboutCtrl {

    constructor(private $scope) {
        console.log(this.$scope)
    }

}

angular.module('openDataHub').controller('AboutCtrl', AboutCtrl);

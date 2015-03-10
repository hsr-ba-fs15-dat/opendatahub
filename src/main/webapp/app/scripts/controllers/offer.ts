/// <reference path='../all.d.ts' />
'use strict';

class OfferCtrl {

    constructor(private $scope, private ExampleService) {
        console.log(this.$scope)
    }

}

angular.module('openDataHub').controller('OfferCtrl', OfferCtrl);

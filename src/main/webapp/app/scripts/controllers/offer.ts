/// <reference path='../../../typings/tsd.d.ts' />
'use strict';


class OfferCtrl {

    constructor(private $scope, private ExampleService) {
        console.log(this.$scope)
    }

}

angular.module('opendatahubApp').controller('OfferCtrl', OfferCtrl);

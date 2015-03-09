/// <reference path='../all.d.ts' />
'use strict';


class MainCtrl {

    constructor(private $scope) {
        console.log(this.$scope)
    }

}

app.controller('MainCtrl', MainCtrl);

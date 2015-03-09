/// <reference path='../all.d.ts' />
'use strict';


class AboutCtrl {

    constructor(private $scope) {
        console.log(this.$scope)
    }

}

app.controller('AboutCtrl', AboutCtrl);

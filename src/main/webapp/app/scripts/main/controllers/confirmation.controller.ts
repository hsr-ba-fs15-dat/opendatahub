/// <reference path='../../all.d.ts' />


module odh.main {
    'use strict';
    export interface IOdhModal {
        buttons: {
            cls: string;
            text: string;
            action: Function;
        }[];
        question: string;
        title: string;
    }
    class ConfirmationController {

        public buttons;
        public question;
        public title;

        constructor(private $log:ng.ILogService, private $state:ng.ui.IStateService, public odhModal:IOdhModal) {
            // controller init
            this.buttons = odhModal.buttons;
            this.question = odhModal.question;
            this.title = odhModal.title;
        }


    }
    angular.module('openDataHub.main').controller('ConfirmationController', ConfirmationController);
}

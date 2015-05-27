/// <reference path='../all.d.ts' />


module odh.utils {
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
    /**
     * OpenDataHub Modal Controller
     */
    class ConfirmationController {

        public buttons;
        public question;
        public title;

        constructor(public odhModal:IOdhModal) {
            // controller init
            this.buttons = odhModal.buttons;
            this.question = odhModal.question;
            this.title = odhModal.title;
        }
    }
    angular.module('openDataHub.utils').controller('ConfirmationController', ConfirmationController);
}

/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class PasswordResetController {

        public complete:boolean;
        public model:any;
        public errors:any;

        constructor(private ValidateService:odh.auth.ValidateService,
                    private AuthenticationService:odh.auth.AuthenticationService) {
            // controller init
            this.complete = false;
            this.model = {'email': ''};


        }

        public resetPassword(formData:any) {
            this.errors = [];
            this.ValidateService.form_validation(formData, this.errors);
            if (!formData.$invalid) {
                this.AuthenticationService.resetPassword(this.model.email)
                    .then(function () {
                        // success case
                        this.complete = true;
                    }, function (data) {
                        // error case
                        this.errors = data;
                    });
            }

        }

    }
    angular.module('openDataHub.auth').controller('PasswordResetController', PasswordResetController);
}

/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class PasswordChangeController {

        public errors: any;
        public model: any;
        public complete:boolean;

        constructor(private ValidateService:odh.auth.ValidateService,
                    private AuthenticationService:odh.auth.AuthenticationService) {
            // controller init
            this.model = {'new_password1': '', 'new_password2': ''};
            this.complete = false;
        }

        public changePassword(formData:any) {
            this.errors = [];
            this.ValidateService.form_validation(formData, this.errors);
            if (!formData.$invalid) {
                this.AuthenticationService.changePassword(this.model.new_password1, this.model.new_password2)
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
    angular.module('openDataHub.auth').controller('PasswordChangeController', PasswordChangeController);
}

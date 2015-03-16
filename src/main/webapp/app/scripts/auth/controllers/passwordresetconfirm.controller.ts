/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class PasswordResetConfirmController {

        public complete:boolean;
        public model:any;
        public errors:any;

        constructor(private ValidateService:odh.auth.ValidateService,
                    private AuthenticationService:odh.auth.AuthenticationService, private $routeParams:any) {
            // controller init
            this.complete = false;
            this.model = {'newPassword1': '', 'newPassword2': ''};


        }

        public confirmReset(formData:any) {
            this.errors = [];
            this.ValidateService.form_validation(formData, this.errors);
            if (!formData.$invalid) {
                this.AuthenticationService.confirmReset(this.$routeParams.getFirstToken(),
                    this.$routeParams.passwordResetToken, this.model.new_password1, this.model.new_password2)
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
    angular.module('openDataHub.auth').controller('PasswordResetConfirmController', PasswordResetConfirmController);
}

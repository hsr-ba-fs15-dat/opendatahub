/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class RegisterController {

        public model:any;
        public errors:any;
        public complete:boolean;

        constructor(private ValidateService:odh.auth.ValidateService,
                    private AuthenticationService:odh.auth.AuthenticationService) {
            // controller init
            this.model = {'username': '', 'password': '', 'email': ''};
            this.errors = [];
            this.complete = false;
        }

        public register(formData:any) {
            this.ValidateService.form_validation(formData, this.errors);
            if (!formData.$invalid) {
                this.AuthenticationService.register(
                    this.model.username, this.model.password1, this.model.password2, this.model.email
                )
                    .then(() => {
                        // success case
                        this.complete = true;
                    })
                    .catch((data) => {
                        // error case
                        this.errors = data;
                    });
            }
        }
    }
    angular.module('openDataHub.auth').controller('RegisterController', RegisterController);
}

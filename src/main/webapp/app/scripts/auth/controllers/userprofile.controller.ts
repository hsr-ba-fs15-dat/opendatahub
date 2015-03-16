/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class UserProfileController {

        public complete:boolean;
        public model:any;
        public errors:any;

        constructor(private ValidateService:odh.auth.ValidateService,
                    private AuthenticationService:odh.auth.AuthenticationService) {
            // controller init
            this.model = {'first_name': '', 'last_name': '', 'email': ''};
            this.complete = false;
            AuthenticationService.profile().then(function (data) {
                this.model = data;
            });
        }

        public updateProfile(formData:any, model:any) {
            this.errors = [];
            this.ValidateService.form_validation(formData, this.errors);
            if (!formData.$invalid) {
                this.AuthenticationService.updateProfile(model)
                    .then(function (data) {
                        // success case
                        this.complete = true;
                    }, function (data) {
                        // error case
                        this.error = data;
                    });
            }
        }


    }
    angular.module('openDataHub.auth').controller('UserProfileController', UserProfileController);
}

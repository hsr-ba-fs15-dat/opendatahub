/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class LoginController {

        public model: any;
        public complete: boolean;
        public errors: any;
        constructor(private $location:ng.ILocationService,
                    private AuthenticationService:odh.auth.AuthenticationService,
                    private ValidateService:odh.auth.ValidateService) {
            this.model = {'username': '', 'password': ''};
            this.complete = false;
        }

        public login(formData:any) {
            this.errors = [];
            this.ValidateService.form_validation(formData, this.errors);
            var that = this;
            if (!formData.$invalid) {
                this.AuthenticationService.login(this.model.username, this.model.password)
                    .then(function (data) {
                        // success case
                        that.$location.path('/');
                    }, function (data) {
                        // error case
                        that.errors = data;
                    });
            }
        }

    }

    angular.module('openDataHub.auth').controller('LoginController', LoginController);
}
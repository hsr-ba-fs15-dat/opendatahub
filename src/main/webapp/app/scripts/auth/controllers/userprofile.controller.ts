/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    class UserProfileController {

        public complete:boolean;
        public model:any;
        public errors:any;
        public error:any;
        public username;

        constructor(public UserService:odh.auth.UserService) {
            // controller init
            this.model = {'first_name': '', 'last_name': '', 'email': '', extra_data : ''};
            this.complete = false;
            UserService.profile().then((data:any) => {
                this.model = data.data;
                this.username = data.data.username;
                console.log(data);
            });
        }

    }
    angular.module('openDataHub.auth').controller('UserProfileController', UserProfileController);
}

/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';
    interface IModel {
        username:string;
        description:string;
    }
    class UserProfileController {

        public complete:boolean;
        public model:IModel;
        public errors:any;
        public error:any;
        public username:string;
        public first_name:string;
        public last_name:string;
        public email:string;
        public profile_photo:string;
        public profile_photo_origin:string;
        public providers:{};


        constructor(public UserService:odh.auth.UserService) {
            // controller init
            this.model = {username: '', description: ''};
            this.complete = false;
            UserService.profile().then((data:any) => {
                this.username = data.data.username;
                this.last_name = data.data.last_name;
                this.first_name = data.data.first_name;
                this.profile_photo = data.data.profile_photo;
                this.profile_photo_origin = data.data.profile_photo_origin;
                this.email = data.data.email;
                this.model.username = data.data.username;
                this.model.description = data.data.username;
                this.providers = data.data.social_auth;
                console.log(data.data);
            });
        }

    }
    angular.module('openDataHub.auth').controller('UserProfileController', UserProfileController);
}

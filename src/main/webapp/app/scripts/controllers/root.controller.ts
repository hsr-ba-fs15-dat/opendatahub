/// <reference path='../all.d.ts' />


module odh {
    'use strict';
    /**
     * responsible for loading the config from the API
     */
    class RootController {
        public showAlert:boolean = true;

        constructor(public AppLoader:odh.utils.AppLoader,
                    private AppConfig:odh.IAppConfig,
                    private ToastService:odh.utils.ToastService,
                    private UserService:auth.UserService,
                    private $window:ng.IWindowService) {
            AppLoader.acquire();

            AppConfig.then((config) => {
                AppLoader.release();
            }).catch((res) => {
                if (res.status === 403) {
                    UserService.removeToken();
                    $window.location.reload();
                } else {
                    ToastService.failure('Etwas ist schief gelaufen. Bitte versuchen Sie es später erneut!');
                }
            });
        }

    }
    angular.module('openDataHub').controller('RootController', RootController);
}

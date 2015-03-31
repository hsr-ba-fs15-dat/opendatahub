/// <reference path='../all.d.ts' />


module odh {
    'use strict';

    class RootController {

        constructor(public AppLoader:odh.utils.AppLoader, private AppConfig:odh.IAppConfig,
                    private ToastService:odh.utils.ToastService, private $auth, private $window:ng.IWindowService) {
            AppLoader.acquire();

            AppConfig.then((config) => {
                AppLoader.release();
            }).catch((res) => {
                if (res.status === 403) {
                    $auth.removeToken();
                    $window.location.reload();
                } else {
                    ToastService.failure('Etwas ist schief gelaufen. Bitte versuchen Sie es später erneut!');
                }
            });
        }

    }
    angular.module('openDataHub').controller('RootController', RootController);
}

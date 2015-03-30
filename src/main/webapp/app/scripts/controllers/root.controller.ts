/// <reference path='../all.d.ts' />


module odh {
    'use strict';

    class RootController {

        constructor(public AppLoader:odh.utils.AppLoader, private AppConfig:odh.IAppConfig,
                    private ToastService:odh.utils.ToastService) {
            AppLoader.acquire();

            AppConfig.then((config) => {
                AppLoader.release();
            }).catch(() => {
                ToastService.failure('Etwas ist schief gelaufen. Bitter versuchen Sie es später erneut!');
            });
        }

    }
    angular.module('openDataHub').controller('RootController', RootController);
}

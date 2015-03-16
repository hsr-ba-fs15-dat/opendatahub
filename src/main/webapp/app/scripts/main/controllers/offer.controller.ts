/// <reference path='../../all.d.ts' />


module odh {
    'use strict';

    export class OfferController {

        public dataSources:{}[];
        public dataSource:{};
        public name:string;
        public description:string;
        public params:any = {};
        public progress = 0;

        constructor(private $http:ng.IHttpService, private $state:ng.ui.IStateService, private $scope:ng.IScope,
                    private ToastService:odh.utils.ToastService, private $window:ng.IWindowService, private $upload) {

            this.dataSources = [{label: 'Online', type: 'online'}, {label: 'Datei hochladen', type: 'file'}];
            this.dataSource = this.dataSources[0];
            this.switchDataSource(this.dataSource, this.dataSource);
        }

        public switchDataSource(item, model) {
            this.$state.go('offer.params', {type: model.type});
        }

        public cancel() {
            this.$state.go('main');
        }

        public submit() {
            // todo restangular or ngresource
            // todo move to service
            // todo redirect to newly created doc "detail view"
            var promise:any;

            if (this.params.file) {
                promise = this.$upload.upload({
                    url: '/api/v1/documents',
                    fields: {name: this.name, description: this.description},
                    file: this.params.file
                });

                promise.progress((event) => {
                    this.progress = (event.loaded / event.total) * 100;
                });

            } else {
                promise = this.$http.post('/api/v1/documents', {
                    name: this.name,
                    description: this.description,
                    url: this.params.url
                });
            }

            promise.then(data => this.createSuccess(data))
                .catch(data => this.createFailure(data));

        }

        private createSuccess(data) {
            // todo remove demo/test
            this.ToastService.success('Datei erfolgreich abgelegt');
            this.$window.open(data.data.url);
            this.$state.go('main');
        }

        private createFailure(data) {
            // todo validation
            this.ToastService.failure('Ups! Irgendwas ist schief gelaufen!');
        }

    }
    angular.module('openDataHub.main').controller('OfferController', OfferController);


    class OfferParamsController {
        public fields:{}[];

        constructor(private $stateParams) {
            // todo refactor
            if ($stateParams.type === 'online') {
                this.fields = [
                    {id: 'url', placeholder: 'http://', label: 'Adresse'}
                ];
            } else {
                this.fields = [
                    {id: 'file', label: 'Wählen Sie Ihre Datei', type: 'file'}
                ];
            }
        }

    }
    angular.module('openDataHub.main').controller('OfferParamsController', OfferParamsController);
}

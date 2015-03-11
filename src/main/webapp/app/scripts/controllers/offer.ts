/// <reference path='../all.d.ts' />
'use strict';

module odh {

    export class OfferController {

        public dataSources:{}[];
        public dataSource:{};
        public name:string;
        public description:string;
        public params:{} = {};

        constructor(private $http:ng.IHttpService, private $state:ng.ui.IStateService, private ngToast, private $window:ng.IWindowService) {
            this.dataSources = [{label: 'Online', type: 'online'}, {label: 'Datei hochladen', type: 'file'}];
            this.dataSource = this.dataSources[0];
            this.switchDataSource(this.dataSource, this.dataSource);
        }

        public switchDataSource(item, model) {
            this.$state.go('offer.params', {type: model.type})
        }

        public cancel() {
            this.$state.go('main');
        }

        public submit() {
            // todo restangular or ngresource

            this.$http.post('/api/v1/documents/', {
                name: this.name,
                description: this.description,
                url: this.params['url']
            })
                .then(data => this.createSuccess(data))
                .catch(data => this.createFailure(data));

        }

        private createSuccess(data) {
            // todo remove demo/test
            this.$window.open(data.data.url);
            this.ngToast.create('Datei erfolgreich abgelegt');

        }

        private createFailure(data) {
            this.ngToast.create({className: 'danger', content: 'Ups! Irgendwas ist schief gelaufen'});
        }

    }

    angular.module('openDataHub').controller('OfferController', OfferController);


    class OfferParamsController {
        public fields:{}[];

        constructor(private $stateParams:ng.ui.IStateParamsService) {
            // TODO refactor
            if ($stateParams['type'] === 'online') {
                this.fields = [
                    {id: 'url', placeholder: 'http://', label: 'Adresse'}
                ];
            } else {

            }
        }

    }

    angular.module('openDataHub').controller('OfferParamsController', OfferParamsController);
}
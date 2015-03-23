/// <reference path='../../all.d.ts' />


module odh {
    'use strict';

    export class OfferController {

        public dataSource:string = 'online';
        public name:string;
        public description:string;
        public isprivate:boolean;
        public params:any = {};
        public progress = 0;
        public submitted:boolean = false;

        constructor(private $http:ng.IHttpService, private $state:ng.ui.IStateService, private $scope:any,
                    private ToastService:odh.utils.ToastService, private $window:ng.IWindowService, private $upload,
                    private UrlService:odh.utils.UrlService) {

        }

        public switchDataSource() {
            this.$state.go('offer.params', {type: this.dataSource});
        }

        public cancel() {
            this.$state.go('main');
        }

        public submit() {
            // todo restangular or ngresource
            // todo move to service
            // todo redirect to newly created doc "detail view"
            this.submitted = true;
            this.$scope.form.$setDirty();
            if (this.$scope.form.$invalid) {
                return;
            }

            var promise:any;
            var url = this.UrlService.get('documents');

            console.log(this.params);

            if (this.params.file) {
                promise = this.$upload.upload({
                    url: url,
                    fields: {name: this.name, description: this.description, 'private':this.isprivate},
                    file: this.params.file
                });

                promise.progress((event) => {
                    this.progress = (event.loaded / event.total) * 100;
                });

            } else {
                promise = this.$http.post(url, {
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
            this.$state.go('document', {id: data.data.id});
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
                    {id: 'file', label: 'Wählen oder ziehen Sie Ihre Datei', type: 'file'}
                ];
            }
        }

    }
    angular.module('openDataHub.main').controller('OfferParamsController', OfferParamsController);
}

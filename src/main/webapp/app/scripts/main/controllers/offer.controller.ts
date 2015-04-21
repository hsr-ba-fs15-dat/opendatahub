/// <reference path='../../all.d.ts' />


module odh {
    'use strict';

    export class OfferController {

        public dataSource:string = 'online';
        public name:string;
        public description:string;
        public isPrivate:boolean;
        public params:any = {};
        public progress = 0;
        public submitted:boolean = false;
        public field:any;

        public refreshChoices = [
            {name: '5 Minuten', value: 300},
            {name: '30 Minuten', value: 1800},
            {name: '1 Stunde', value: 3600},
            {name: '6 Stunden', value: 21600},
            {name: '1 Tag', value: 86400}
        ];

        public formatChoices = [];

        private fieldsByType = {
            online: {
                id: {url: 'url', refresh: 'url.refresh', format: 'url.format'},
                placeholder: {url: 'http://'},
                label: {url: 'Adresse', refresh: 'Abfrage-Intervall', format: 'Format'},
                defaults: {refresh: 3600}
            },
            file: {id: 'file', label: 'Wählen oder ziehen Sie Ihre Dateien', type: 'file'}
        };

        constructor(private $http:ng.IHttpService, private $state:ng.ui.IStateService, private $scope:any,
                    private ToastService:odh.utils.ToastService, private $window:ng.IWindowService, private $upload,
                    private UrlService:odh.utils.UrlService, private FormatService:odh.main.FormatService) {
            this.switchDataSource();

            FormatService.getAvailableFormats().then(formatList => {
                this.formatChoices = formatList.data;
                this.formatChoices.sort((a, b) => a.label < b.label ? -1 : a.label === b.label ? 0 : 1);
            });
        }

        public switchDataSource() {
            this.field = this.fieldsByType[this.dataSource];

            for (var prop in this.field.defaults) {
                if (this.field.defaults.hasOwnProperty(prop)) {
                    this.params[prop] = this.field.defaults[prop];
                }
            }
        }

        public cancel() {
            this.$state.go('main');
        }

        public submit() {
            // todo restangular or ngresource
            // todo move to service

            this.submitted = true;
            this.$scope.form.$setDirty();

            if (this.$scope.form.$invalid) {
                return;
            }

            var promise:any;
            var url = this.UrlService.get('document');

            if (this.params.file) {
                promise = this.$upload.upload({
                    url: url,
                    fields: {name: this.name, description: this.description, 'private': this.isPrivate},
                    file: this.params.file
                });

                promise.progress((event) => {
                    this.progress = (event.loaded / event.total) * 100;
                });

            } else {
                promise = this.$http.post(url, {
                    name: this.name,
                    description: this.description,
                    url: this.params.url,
                    refresh: this.params.refresh,
                    format: this.params.format
                });
            }

            promise.then(data => this.createSuccess(data))
                .catch(data => this.createFailure(data));

        }

        private createSuccess(data) {
            // todo remove demo/test
            this.ToastService.success('Ihre Daten wurden gespeichert ');
            this.$state.go('document', {id: data.data.id});
        }

        private createFailure(data) {
            // todo validation
            this.ToastService.failure('Ups! Irgendwas ist schief gelaufen!');
        }

    }
    angular.module('openDataHub.main').controller('OfferController', OfferController);

}

/// <reference path='../../all.d.ts' />


module odh {
    'use strict';

    class DocumentListController {

        public searchTerms:string;
        public documents;
        public totalItems:number;
        public currentPage:number = 1;

        constructor(private $scope:ng.IScope, private $log:ng.ILogService, private documentService:odh.DocumentService,
                    private ToastService:odh.utils.ToastService) {

            this.retrieveDataAsync();
        }

        public pageChanged() {
            this.retrieveDataAsync();
        }

        public retrieveDataAsync() {
            this.$log.debug('Fetching data');
            this.documentService.search(this.searchTerms, this.currentPage)
                .then(data => {
                    this.documents = data;
                    this.totalItems = data.meta.count;
                    this.$log.debug('Data: ', data);
                })
                .catch(error => this.onError(error));
        }

        private onError(error) {
            this.ToastService.failure('Suche fehlgeschlagen');
            this.$log.error(error);
        }

    }

    class DocumentDetailController {
        public documentId:number;
        public document;
        public availableFormats:odh.main.IFormat[];

        constructor(private $log:ng.ILogService, private $state:ng.ui.IStateService,
                    private $stateParams:any, private $window:ng.IWindowService,
                    private documentService:odh.DocumentService, private ToastService:odh.utils.ToastService,
                    private FormatService:odh.main.FormatService) {
            this.documentId = $stateParams.id;
            this.retrieveData();
        }

        private retrieveData() {
            this.FormatService.getAvailableFormats().then((data) => {
                this.availableFormats = data.data;
            });

            if (typeof(this.documentId) !== 'undefined') {
                this.document = this.documentService.get(this.documentId)
                    .then(data => {
                        this.document = data;
                    })
                    .catch(error => {
                        this.ToastService.failure('Dokument wurde nicht gefunden');
                        this.$log.error(error);
                    });
            }
        }

    }

    angular.module('openDataHub.main')
        .controller('DocumentListController', DocumentListController)
        .controller('DocumentDetailController', DocumentDetailController);

}

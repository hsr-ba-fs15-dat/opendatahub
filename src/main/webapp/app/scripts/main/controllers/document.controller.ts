/// <reference path='../../all.d.ts' />


module odh {
    'use strict';

    class DocumentListController {

        public searchTerms:string;
        public documents;

        public gridOptions = {
            data: 'docs.documents.results',
            totalServerItems: 'docs.documents.count',
            enablePaging: true,
            enableRowSelection: false,
            showFooter: true,
            columnDefs: [
                {field: 'name', displayName: 'Name',
                    cellTemplate: '<div class="ngCellText">' +
                    '<a ui-sref="document({id: row.getProperty(\'id\')})">{{row.getProperty(col.field)}}</a>' +
                    '</div>'},
                {field: 'description', displayName: 'Beschreibung'}
            ],
            pagingOptions: {
                pageSizes: [50],
                pageSize: 50,
                currentPage: 1
            }
        };

        constructor(private $scope:ng.IScope, private $log:ng.ILogService, private documentService:odh.DocumentService,
                    private ToastService:odh.utils.ToastService) {

            $scope.$watch(() => this.gridOptions.pagingOptions.currentPage,
                <any>angular.bind(this, this.pagingOptionsChanged));
            this.retrieveDataAsync();
        }

        public retrieveDataAsync() {
            this.$log.debug('Fetching data');
            this.documentService.search(this.searchTerms, this.gridOptions.pagingOptions.currentPage)
                .then(data => {
                    this.documents = data;
                    this.$log.debug('Data: ', data);
                    if (!this.$scope.$$phase) {
                        this.$scope.$apply();
                    }
                })
                .catch(error => this.onError(error));
        }

        private pagingOptionsChanged(newVal, oldVal) {
            if (newVal !== oldVal) {
                this.retrieveDataAsync();
            }
        }

        private onError(error) {
            this.ToastService.failure('Suche fehlgeschlagen');
            this.$log.error(error);
        }

    }

    class DocumentDetailController {
        private documentId:number;
        private document;

        constructor(private $log:ng.ILogService, private $state:ng.ui.IStateService,
                    private $stateParams:any, private $window:ng.IWindowService,
                    private documentService:odh.DocumentService, private ToastService:odh.utils.ToastService) {
            this.documentId = $stateParams.id;

            this.retrieveData();
        }

        private retrieveData() {
            if (typeof(this.documentId) !== 'undefined') {
                this.documentService.get(this.documentId)
                    .then(data => this.document = data)
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

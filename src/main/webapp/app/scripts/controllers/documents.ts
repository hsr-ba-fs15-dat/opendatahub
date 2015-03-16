/// <reference path='../all.d.ts' />


module odh {
    'use strict';

    interface IDocumentList {
        results: IDocument[];
        count: number;
    }

    class DocumentListController {

        public searchTerms:string;
        public documents:IDocumentList;

        public gridOptions = {
            data: 'docs.documents.results',
            totalServerItems: 'docs.documents.count',
            enablePaging: true,
            showFooter: true,
            columnDefs: [
                {field: 'name', displayName: 'Name'},
                {field: 'description', displayName: 'Beschreibung'}
            ],
            pagingOptions: {
                pageSizes: [50],
                pageSize: 50,
                currentPage: 1
            }
        };

        constructor(private $scope:ng.IScope, private $log:ng.ILogService, private $state:ng.ui.IStateService,
                    private documentService:odh.DocumentService, private ToastService:odh.utils.ToastService) {

            $scope.$watch(() => this.gridOptions.pagingOptions.currentPage,
                <any>angular.bind(this, this.pagingOptionsChanged));
            this.retrieveDataAsync();
        }

        public retrieveDataAsync() {
            this.$log.debug('Fetching data');
            this.documentService.$get(this.searchTerms, this.gridOptions.pagingOptions.currentPage)
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
    angular.module('openDataHub').controller('DocumentListController', DocumentListController);
}

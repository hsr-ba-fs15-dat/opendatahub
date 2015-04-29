/// <reference path='../../all.d.ts' />


module odh {
    'use strict';

    class DocumentListController {

        public tableParams:any;
        public loading = true;

        constructor(private $log:ng.ILogService, private DocumentService:odh.main.DocumentService,
                    private ToastService:odh.utils.ToastService,
                    private $auth:any, private ngTableParams) {
            this.tableParams = new ngTableParams({
                    page: 1,
                    count: 50,
                    limit: 50
                },
                {
                    counts: [10, 25, 50, 100],
                    total: 0,
                    getData: ($defer, params) => {
                        this.DocumentService.getList(params.url()).then(result => {
                            params.total(result.count);
                            $defer.resolve(result.results);
                            this.loading = false;
                        }).catch(error => this.onError(error));
                    }
                });
        }

        public isAuthenticated() {
            return this.$auth.isAuthenticated();
        }

        private onError(error) {
            this.loading = false;
            this.ToastService.failure('Suche fehlgeschlagen');
            this.$log.error(error);
        }

    }

    class DocumentDetailController {
        public documentId:number;

        public document;
        public fileGroups;
        public loading = true;

        public availableFormats:odh.main.IFormat[];

        constructor(private $log:ng.ILogService, private $stateParams:any, private $window:ng.IWindowService,
                    private DocumentService:odh.main.DocumentService, private ToastService:odh.utils.ToastService,
                    private FormatService:odh.main.FormatService, private FileGroupService:odh.main.FileGroupService) {
            this.documentId = $stateParams.id;
            this.retrieveData();
        }

        public downloadAs(group, formatName) {
            this.$log.debug('Triggered download of ', group, 'as', formatName);
            group.canDownload(formatName).then(() => {
                this.$window.location.href = group.data + '?fmt=' + formatName;
            }).catch(() => {
                this.ToastService.failure('Die Datei konnte nicht ins gewünschte Format konvertiert werden.');
            });

        }

        private retrieveData() {
            this.FormatService.getAvailableFormats().then((data) => {
                this.availableFormats = data.data;
            });

            if (typeof(this.documentId) !== 'undefined') {
                this.document = this.DocumentService.get(this.documentId)
                    .then(data => {
                        this.$log.debug('Document ' + this.documentId, data);
                        this.document = data;
                    })
                    .catch(error => {
                        this.ToastService.failure('Dokument wurde nicht gefunden');
                        this.$log.error(error);
                    });

                this.fileGroups = this.FileGroupService.getAll(this.documentId, true)
                    .then(data => {
                        this.$log.debug('File Groups for document ' + this.documentId, data);
                        this.fileGroups = data;
                        this.loading = false;
                    })
                    .catch(error => {
                        this.ToastService.failure('Keine Daten gefunden für dieses Dokument');
                        this.$log.error(error);
                    });
            }
        }
    }

    angular.module('openDataHub.main')
        .controller('DocumentListController', DocumentListController)
        .controller('DocumentDetailController', DocumentDetailController);

}

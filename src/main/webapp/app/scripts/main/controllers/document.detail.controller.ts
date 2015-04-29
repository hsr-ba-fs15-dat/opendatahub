/// <reference path='../../all.d.ts' />

module odh.main {

    class DocumentDetailController {
        public documentId:number;

        public pkg;
        public fileGroups;
        public loading = true;

        public availableFormats;

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
            this.availableFormats = this.FormatService.getAvailableFormats();

            if (typeof(this.documentId) !== 'undefined') {
                this.pkg = this.DocumentService.get(this.documentId)
                    .then(data => {
                        this.$log.debug('Document ' + this.documentId, data);
                        this.pkg = data;
                    })
                    .catch(error => {
                        this.ToastService.failure('Dokument wurde nicht gefunden');
                        this.$log.error(error);
                    });

                this.fileGroups = this.FileGroupService.getAll(this.documentId, true)
                    .then(data => {
                        this.$log.debug('File Groups for Document ' + this.documentId, data);
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
        .controller('DocumentDetailController', DocumentDetailController);
}

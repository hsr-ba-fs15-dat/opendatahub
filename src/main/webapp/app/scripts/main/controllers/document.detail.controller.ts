/// <reference path='../../all.d.ts' />

module odh.main {

    class DocumentDetailController {
        public documentId:number;

        public pkg;
        public fileGroups;
        public loading = true;
        public allowDelete = false;
        public availableFormats;
        public previewSuccess:boolean = false;

        constructor(private $log:ng.ILogService, private $stateParams:any, private $window:ng.IWindowService,
                    private DocumentService:odh.main.DocumentService, private ToastService:odh.utils.ToastService,
                    private FormatService:odh.main.FormatService, private FileGroupService:odh.main.FileGroupService,
                    private PackageService:main.PackageService, private $auth:any,
                    private $modal:ng.ui.bootstrap.IModalService,
                    private $state:ng.ui.IStateService) {
            this.documentId = $stateParams.id;
            this.retrieveData();
            this.FormatService.getAvailableFormats().then(data => {
                var results = this.FormatService.sortByLabel(data.data);
                results.push({
                    name: null, label: 'Original', description: 'Unveränderte Daten', example: null,
                    extension: null
                });
                this.availableFormats = results;
            });
        }

        public downloadAs(group, formatName) {
            this.$log.debug('Triggered download of ', group, 'as', formatName);
            group.canDownload(formatName).then(() => {
                this.$window.location.href = group.data + ( formatName ? '?fmt=' + formatName : '');
            }).catch(() => {
                this.ToastService.failure('Die Datei konnte nicht ins gewünschte Format konvertiert werden.');
            });
        }

        public remove() {
            var instance = this.$modal.open({
                templateUrl: 'views/deleteconfirmation.html',
                controller: 'DeleteTransformationController as vm',
                resolve: {
                    docId: this.documentId
                }
            });
            instance.result.then(() => {
                    this.DocumentService.remove({id: this.documentId}).then(() =>
                            this.$state.go('packages')
                    ).catch((err) =>
                            this.ToastService.failure('Beim Löschen des Dokumentes ist ein Fehler aufgetreten.')
                    );
                }
            );
        }

        public update() {
            this.DocumentService.update(this.pkg);
        }

        public getRefreshRate(refreshrate:number) {
            refreshrate = refreshrate / 60;
            if (refreshrate < 60) {
                return refreshrate + ' Minuten';
            }
            refreshrate = refreshrate / 60;
            if (refreshrate < 24) {
                return refreshrate + (refreshrate === 1 ? ' Stunde' : ' Stunden');
            }
            refreshrate = refreshrate / 24;

            return refreshrate + (refreshrate === 1 ? ' Tag' : ' Tage');

        }

        private retrieveData() {
            if (typeof(this.documentId) !== 'undefined') {
                this.pkg = this.DocumentService.get(this.documentId)
                    .then(data => {
                        this.$log.debug('Document ' + this.documentId, data);
                        this.pkg = data;
                        this.allowDelete = this.$auth.isAuthenticated() &&
                        data.owner.id === this.$auth.getPayload().user_id;

                        console.log(data);
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

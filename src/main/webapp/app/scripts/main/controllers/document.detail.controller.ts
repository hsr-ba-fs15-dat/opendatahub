/// <reference path='../../all.d.ts' />

module odh.main {

    class DocumentDetailController {
        /**
         * @identifier
         */
        public documentId:number;
        /**
         * Document container
         * @type {Object}
         */
        public pkg;
        /**
         * fileGroups corresponding with this document
         * @type {Array}
         */
        public fileGroups:any[];
        /**
         * document is loading
         * @type {boolean}
         */
        public loading:boolean = true;
        /**
         * deletion by this user is allowed. (Also editing)
         * @type {boolean}
         */
        public allowDelete:boolean = false;
        /**
         * List of available formats
         * @type {Array}
         */
        public availableFormats:{
            name: string;
            label: string;
            description: string;
            example: string;
            extension: string;
        }[];
        /**
         * Preview rendered successful
         * @type {boolean}
         */
        public previewSuccess:boolean = false;

        constructor(private $log:ng.ILogService, private $stateParams:any, private $window:ng.IWindowService,
                    private DocumentService:odh.main.DocumentService, private ToastService:odh.utils.ToastService,
                    private FormatService:odh.main.FormatService, private FileGroupService:odh.main.FileGroupService,
                    private PackageService:odh.main.PackageService,
                    private $auth:any,
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

        /**
         *
         * @param group fileGroup
         * @param formatName
         */
        public downloadAs(group, formatName:string) {
            this.$log.debug('Triggered download of ', group, 'as', formatName);
            this.PackageService.download(group, formatName);
        }

        /**
         * opens Modal window and asks for deletion.
         */
        public remove() {
            var modalInstance;
            var odhModal:utils.IOdhModal = {
                buttons: [{
                    text: 'Löschen',
                    cls: 'btn-warning',
                    action: () => {
                        modalInstance.close();
                    }
                },
                    {
                        text: 'Abbrechen',
                        cls: 'btn-primary',
                        action: () => {
                            modalInstance.dismiss();
                        }
                    }],
                question: 'Möchten Sie dieses Dokument wirklich löschen?',
                title: 'Sind Sie sicher?'


            };
            modalInstance = this.$modal.open({
                animation: true,
                templateUrl: 'views/helpers/confirmation.html',
                controller: 'ConfirmationController as cc',
                resolve: {
                    odhModal: () => {
                        return odhModal;
                    }

                }
            });
            modalInstance.result.then(() => {
                    this.DocumentService.remove({id: this.documentId}).then(() => {
                            this.$state.go('packages');
                            this.ToastService.success('Dokument gelöscht.');
                        }
                    ).catch((err) =>
                            this.ToastService.failure('Beim Löschen des Dokumentes ist ein Fehler aufgetreten.')
                    );
                }
            );
        }

        /**
         * updates current package in the database
         */
        public update() {
            this.DocumentService.update(this.pkg);
        }

        /**
         * calculates refresh rate based on entered seconds
         * @param refreshrate
         * @returns {string}
         */
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

        /**
         * fetches data from API
         */
        private retrieveData() {
            if (typeof(this.documentId) !== 'undefined') {
                this.DocumentService.get(this.documentId)
                    .then(data => {
                        this.$log.debug('Document ' + this.documentId, data);
                        this.pkg = data;
                        this.allowDelete = this.$auth.isAuthenticated() &&
                        data.owner.id === this.$auth.getPayload().user_id;
                    })
                    .catch(error => {
                        this.ToastService.failure('Dokument wurde nicht gefunden');
                        this.$log.error(error);
                    });

                this.FileGroupService.getAll(this.documentId, true)
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

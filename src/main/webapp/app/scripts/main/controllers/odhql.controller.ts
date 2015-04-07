/// <reference path='../../all.d.ts' />


module odh {
    'use strict';

    export class OdhQLController {

        public query:string;
        public columns:string[];
        public rows:{};
        public submitted:boolean = false;
        public fg;
        public fileGroups;
        public odhsqlinput = '';
        public uniqueName;

        constructor(private $http:ng.IHttpService, private $state:ng.ui.IStateService, private $scope:any,
                    private ToastService:odh.utils.ToastService, private $window:ng.IWindowService, private $upload,
                    private UrlService:odh.utils.UrlService, private FileGroupService:main.FileGroupService,
                    private $log:ng.ILogService) {

        }

        public insert(col) {
            console.log(col);
            this.odhsqlinput += this.uniqueName + '.' + col;
        }

        public getFileGroup(documentId:any, uniqueName:string) {
            this.uniqueName = uniqueName;
            this.fileGroups = this.FileGroupService.getAll(documentId, true)
                .then(data => {
                    this.$log.debug('File Groups for document ' + documentId, data);
                    this.fileGroups = data;
                })
                .catch(error => {
                    this.ToastService.failure('Keine Daten gefunden für dieses Dokument');
                    this.$log.error(error);
                });
            console.log(this.fileGroups);
            return this.fileGroups;
        }

        public cancel() {
            this.$state.go('main');
        }

        public execute() {
            this.$http.get(this.UrlService.get('odhql'), {params: {query: this.query}}).then((data:any) => {
                this.columns = data.data.columns;
                this.rows = data.data.data;
            });
        }

    }
    angular.module('openDataHub.main').controller('OdhQLController', OdhQLController);

}

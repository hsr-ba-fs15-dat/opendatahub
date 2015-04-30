'use strict';

describe('Controller: TransformationCreateController', function () {

    // load the controller's module
    beforeEach(module('openDataHub'));

    var TransformationCreateController,
        scope, $q,
        $httpBackend;
    var document = {id: 1};
    var FileGroupService;
    // Initialize the controller and a mock scope
    beforeEach(inject(function ($controller, $rootScope, _$httpBackend_, _$q_, _FileGroupService_) {
        scope = $rootScope.$new();
        //FileGroupService = jasmine.createSpyObj('FileGroupService', ['getAll']);
        $httpBackend = _$httpBackend_;
        $q = _$q_;
        FileGroupService = _FileGroupService_;
        TransformationCreateController = $controller('TransformationCreateController', {
            $scope: scope,
            FileGroupService: FileGroupService
        });
    }));
    /*
    it('should get the Filegroups', function () {

    });

    it('should modify the object', function () {
        var d = $q.defer();
        spyOn(FileGroupService, 'getAll').and.returnValue(d.promise);
        TransformationCreateController.getFileGroup(document, 3);
        var fileGroup = [{id: 4, preview: {}}, {id: 5, preview: {}}];
        d.resolve(fileGroup);
        expect(FileGroupService.getAll).toHaveBeenCalledWith(1, true, 3);
    });
     */
});

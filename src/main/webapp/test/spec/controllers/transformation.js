'use strict';

describe('Controller: TransformationCreateController', function () {

    // load the controller's module
    beforeEach(module('openDataHub'));

    var TransformationCreateController,
        scope;

    // Initialize the controller and a mock scope
    beforeEach(inject(function ($controller, $rootScope) {
        scope = $rootScope.$new();
        TransformationCreateController = $controller('TransformationCreateController', {
            $scope: scope
        });
    }));

    it('should be private', function () {


        // scope.selected.add(demo);
        // expect(scope.selected.items[0]).toBe(demo);
    });
});

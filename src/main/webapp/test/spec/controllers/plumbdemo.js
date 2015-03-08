'use strict';

describe('Controller: PlumbdemoCtrl', function () {

  // load the controller's module
  beforeEach(module('opendatahubApp'));

  var PlumbdemoCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    PlumbdemoCtrl = $controller('PlumbdemoCtrl', {
      $scope: scope
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(scope.awesomeThings.length).toBe(3);
  });
});
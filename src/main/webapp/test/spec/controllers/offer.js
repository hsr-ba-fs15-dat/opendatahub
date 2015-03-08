'use strict';

describe('Controller: OfferCtrl', function () {

  // load the controller's module
  beforeEach(module('opendatahubApp'));

  var OfferCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    OfferCtrl = $controller('OfferCtrl', {
      $scope: scope
    });
  }));

  it('should ... todo', function () {
    expect(true).toBe(true);
  });
});

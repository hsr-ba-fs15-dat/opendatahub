/// <reference path='../../../../typings/tsd.d.ts' />
(function () {
  'use strict';

  angular
    .module('openDataHub.auth.services')
    .factory('Users', Users);

  Users.$inject = ['$http'];

  function Users($http) {
    var Users = {
      all: all
    };

    return Users;

    function all() {
      return $http.get('/api/v1/users/');
    }
  }
})();
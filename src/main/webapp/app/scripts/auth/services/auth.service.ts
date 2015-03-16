/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    export class AuthenticationService {

        constructor(private $cookies, private $http:ng.IHttpService,
                   private $q:ng.IQService, private $rootScope:ng.IRootScopeService) {

        }

        API_URL = '/rest-auth';
        use_session = true;
        authenticated = null;
        authPromise = null;

        public request(args) {
            if (this.$cookies.token) {
                this.$http.defaults.headers.common.Authorization = 'Token ' + this.$cookies.token;
            }
            // continue
            var params = args.params || {};
            args = args || {};
            var deferred = this.$q.defer(),
                url = this.API_URL + args.url,
                method = args.method || 'GET',
                data = args.data || {};
            //
            console.log(url);
            this.$http({
                url: url,
                withCredentials: this.use_session,
                method: method.toUpperCase(),
                headers: {'X-CSRFToken': this.$cookies.csrftoken},
                params: params,
                data: data
            })
                .then((data) => {
                    deferred.resolve(data);
                })
                .catch((data: any) => {
                    deferred.reject(data.data);
                })
                ;
            return deferred.promise;
        }

        public register(username, password1, password2, email, more = null) {
            var data = {
                'username': username,
                'password1': password1,
                'password2': password2,
                'email': email
            };
            data = angular.extend(data, more);
            return this.request({
                'method': 'POST',
                'url': '/registration/',
                'data': data
            });
        }

        public login(username, password) {
            var AuthenticationService = this;
            return this.request({
                'method': 'POST',
                'url': '/login/',
                'data': {
                    'username': username,
                    'password': password
                }
            }).then((data: any) => {
                if (!AuthenticationService.use_session) {
                    this.$http.defaults.headers.common.Authorization = 'Token ' + data.key;
                    this.$cookies.token = data.key;
                }
                AuthenticationService.authenticated = true;
                this.$rootScope.$broadcast('djangoAuth.logged_in', data);
            });
        }

        public logout() {
            return this.request({
                'method': 'POST',
                'url': '/logout/'
            }).then(() => {
                delete this.$http.defaults.headers.common.Authorization;
                delete this.$cookies.token;
                this.authenticated = false;
                this.$rootScope.$broadcast('djangoAuth.logged_out');
            });
        }

        public changePassword(password1, password2) {
            return this.request({
                'method': 'POST',
                'url': '/password/change/',
                'data': {
                    'new_password1': password1,
                    'new_password2': password2
                }
            });
        }


        public resetPassword(email) {
            return this.request({
                'method': 'POST',
                'url': '/password/reset/',
                'data': {
                    'email': email
                }
            });
        }

        public profile() {
            return this.request({
                'method': 'GET',
                'url': '/user/'
            });
        }

        public updateProfile(data) {
            return this.request({
                'method': 'PATCH',
                'url': '/user/',
                'data': data
            });
        }

        public verify(key) {
            return this.request({
                'method': 'POST',
                'url': '/registration/verify-email/',
                'data': {'key': key}
            });
        }

        public confirmReset(uid, token, password1, password2) {
            return this.request({
                'method': 'POST',
                'url': '/password/reset/confirm/',
                'data': {
                    'uid': uid,
                    'token': token,
                    'new_password1': password1,
                    'new_password2': password2
                }
            });
        }

        public authenticationStatus(restrict = false, force = false) {
            if (this.authPromise == null || force) {
                this.authPromise = this.request({
                    'method': 'GET',
                    'url': '/user/'
                });
            }
            var da = this;
            var getAuthStatus = this.$q.defer();
            if (this.authenticated != null && !force) {
                // we have a stored value which means we can pass it back right away.
                if (this.authenticated === false && restrict) {
                    getAuthStatus.reject('User is not logged in.');
                } else {
                    getAuthStatus.resolve();
                }
            } else {
                // there isn't a stored value, or we're forcing a request back to
                // the API to get the authentication status.
                this.authPromise.then(function () {
                    da.authenticated = true;
                    getAuthStatus.resolve();
                }, function () {
                    da.authenticated = false;
                    if (restrict) {
                        getAuthStatus.reject('User is not logged in.');
                    } else {
                        getAuthStatus.resolve();
                    }
                });
            }
            return getAuthStatus.promise;
        }

        public initialize(url, sessions) {
            this.API_URL = url;
            this.use_session = sessions;
            return this.authenticationStatus();
        }

    }
    angular.module('openDataHub').service('AuthenticationService', AuthenticationService);
}


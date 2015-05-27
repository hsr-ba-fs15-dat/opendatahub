// Karma configuration
// http://karma-runner.github.io/0.12/config/configuration-file.html
// Generated on 2015-02-25 using
// generator-karma 0.9.0

module.exports = function(config) {
  'use strict';

  config.set({
    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,

    // base path, that will be used to resolve files and exclude
    basePath: '../',

    // testing framework to use (jasmine/mocha/qunit/...)
    frameworks: ['jasmine'],

    // list of files / patterns to load in the browser
    files: [
      // bower:js
      'bower_components/es5-shim/es5-shim.js',
      'bower_components/jquery/dist/jquery.js',
      'bower_components/angular/angular.js',
      'bower_components/bootstrap/dist/js/bootstrap.js',
      'bower_components/angular-animate/angular-animate.js',
      'bower_components/angular-aria/angular-aria.js',
      'bower_components/angular-cookies/angular-cookies.js',
      'bower_components/angular-messages/angular-messages.js',
      'bower_components/angular-route/angular-route.js',
      'bower_components/angular-sanitize/angular-sanitize.js',
      'bower_components/angular-touch/angular-touch.js',
      'bower_components/angular-ui-router/release/angular-ui-router.js',
      'bower_components/ngtoast/dist/ngToast.js',
      'bower_components/angular-bootstrap/ui-bootstrap-tpls.js',
      'bower_components/angular-ui-utils/ui-utils.js',
      'bower_components/angular-ui-select/dist/select.js',
      'bower_components/ng-file-upload/angular-file-upload.js',
      'bower_components/json3/lib/json3.min.js',
      'bower_components/bootstrap-material-design/dist/js/material.js',
      'bower_components/bootstrap-material-design/dist/js/ripples.js',
      'bower_components/arrive/src/arrive.js',
      'bower_components/angular-easyfb/angular-easyfb.js',
      'bower_components/lodash/dist/lodash.compat.js',
      'bower_components/restangular/dist/restangular.js',
      'bower_components/satellizer/satellizer.js',
      'bower_components/blockui/jquery.blockUI.js',
      'bower_components/angular-truncate/src/truncate.js',
      'bower_components/ng-table/dist/ng-table.min.js',
      'bower_components/ace-builds/src-noconflict/ace.js',
      'bower_components/ace-builds/src-noconflict/mode-sql.js',
      'bower_components/angular-ui-ace/ui-ace.js',
      'bower_components/moment/moment.js',
      'bower_components/moment/locale/de.js',
      'bower_components/angular-moment/angular-moment.js',
      'bower_components/stacktrace-js/stacktrace.js',
      'bower_components/ES6StringFormat/ES6StringFormat.js',
      'bower_components/angular-scroll/angular-scroll.js',
      'bower_components/highlightjs/highlight.pack.js',
      'bower_components/angular-highlightjs/build/angular-highlightjs.js',
      'bower_components/angular-mocks/angular-mocks.js',
      // endbower
      // injector:js
      'app/scripts/odh.module.js',
      'app/scripts/utils/utils.module.js',
      'app/scripts/main/main.module.js',
        'app/scripts/auth/auth.module.js',
      
      'app/scripts/overrides.js',
      'app/scripts/utils/spinner.directive.js',
      'app/scripts/utils/pagination.js',
      'app/scripts/utils/focus.js',
      'app/scripts/utils/confirmation.controller.js',
      'app/scripts/utils/block.directive.js',
      'app/scripts/utils/apploader.service.js',
      'app/scripts/services/appconfig.service.js',
      'app/scripts/utils/warnings.service.js',
      'app/scripts/utils/url.service.js',
      'app/scripts/utils/toast.service.js',
      'app/scripts/controllers/root.controller.js',
        'app/scripts/main/controllers/transformation.create.controller.js',
        'app/scripts/main/services/document.service.js',
      'app/scripts/main/services/transformation.selection.service.js',
      'app/scripts/main/services/transformation.service.js',
        'app/scripts/main/directives/transformation.validation.js',
        'app/scripts/main/directives/transformation.chooser.js',
      'app/scripts/main/directives/preview.js',
      'app/scripts/main/controllers/transformation.detail.controller.js',
        'app/scripts/main/services/package.service.js',
        'app/scripts/main/controllers/package.controller.js',
      'app/scripts/main/controllers/offer.controller.js',
      'app/scripts/main/controllers/navbar.controller.js',
      'app/scripts/main/controllers/document.detail.controller.js',
      'app/scripts/auth/services/user.service.js',
      'app/scripts/auth/controllers/userprofile.controller.js',
      'app/scripts/auth/controllers/login.controller.js',
        'app/scripts/main/services/format.service.js',
      // endinjector
      'test/mock/**/*.js',
      'test/spec/**/*.js'
    ],

    // list of files / patterns to exclude
    exclude: [
    ],

    // web server port
    port: 8080,

    // Start these browsers, currently available:
    // - Chrome
    // - ChromeCanary
    // - Firefox
    // - Opera
    // - Safari (only Mac)
    // - PhantomJS
    // - IE (only Windows)
    browsers: [
      'PhantomJS'
    ],

    // Which plugins to enable
    plugins: [
      'karma-phantomjs-launcher',
      'karma-jasmine'
    ],

    // Continuous Integration mode
    // if true, it capture browsers, run tests and exit
    singleRun: false,

    colors: true,

    // level of logging
    // possible values: LOG_DISABLE || LOG_ERROR || LOG_WARN || LOG_INFO || LOG_DEBUG
    logLevel: config.LOG_INFO,

    // Uncomment the following lines if you are using grunt's server to run the tests
    // proxies: {
    //   '/': 'http://localhost:9000/'
    // },
    // URL root prevent conflicts with the site root
    // urlRoot: '_karma_'
  });
};

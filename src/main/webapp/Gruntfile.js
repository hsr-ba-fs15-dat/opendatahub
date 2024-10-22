// Generated on 2015-02-25 using generator-angular 0.11.1
'use strict';

// # Globbing
// for performance reasons we're only matching one level down:
// 'test/spec/{,*/}*.js'
// use this if you want to recursively match all subfolders:
// 'test/spec/**/*.js'

module.exports = function (grunt) {

    // Load grunt tasks automatically
    require('load-grunt-tasks')(grunt);

    // Time how long tasks take. Can help when optimizing build times
    require('time-grunt')(grunt);

    // Configurable paths for the application
    var appConfig = {
        app: require('./bower.json').appPath || 'app',
        dist: 'dist'
    };
    grunt.loadNpmTasks('grunt-typedoc');
    // Define the configuration for all the tasks
    grunt.initConfig({

        // Project settings
        yeoman: appConfig,
        typedoc: {
            build: {
                options: {
                    module: 'commonjs',
                    out: './docs',
                    name: 'OpenDataHub',
                    target: 'es5',
                    mode: 'file'
                },
                src: ['<%= yeoman.app %>/scripts/**/*.ts']
            }
        },
        // Watches files for changes and runs tasks based on the changed files
        watch: {
            typedoc: {
                files: ['<%= yeoman.app %>/scripts/**/*.ts'],
                tasks: ['typedoc']
            },
            bower: {
                files: ['bower.json'],
                tasks: ['wiredep']
            },
            js: {
                files: ['<%= yeoman.app %>/scripts/{,*/}*.js'],
                tasks: ['newer:jshint:all'],
                options: {
                    livereload: '<%= connect.options.livereload %>'
                }
            },
            //jsTest: {
            //    files: ['test/spec/{,*/}*.js'],
            //    tasks: ['newer:jshint:test', 'karma']
            //},
            compass: {
                files: ['<%= yeoman.app %>/styles/{,*/}*.{scss,sass}'],
                tasks: ['compass:server', 'autoprefixer']
            },
            less: {
                files: ['<%= yeoman.app %>/styles/{,*/}*.less'],
                tasks: ['less:server', 'autoprefixer']
            },
            gruntfile: {
                files: ['Gruntfile.js']
            },
            livereload: {
                options: {
                    livereload: '<%= connect.options.livereload %>'
                },
                files: [
                    '<%= yeoman.app %>/{,*/}*.html',
                    '.tmp/styles/{,*/}*.css',
                    '<%= yeoman.app %>/images/{,*/}*.{png,jpg,jpeg,gif,webp,svg}'
                ]
            }
        },

        // The actual grunt server settings
        connect: {
            options: {
                port: 9000,
                // Change this to '0.0.0.0' to access the server from outside.
                hostname: 'localhost',
                livereload: 35729
            },
            livereload: {
                options: {
                    open: true,
                    middleware: function (connect) {
                        return [
                            connect.static('.tmp'),
                            connect().use(
                                '/bower_components',
                                connect.static('./bower_components')
                            ),
                            connect().use(
                                '/app/styles',
                                connect.static('./app/styles')
                            ),
                            connect.static(appConfig.app)
                        ];
                    }
                }
            },
            //test: {
            //    options: {
            //        port: 9001,
            //        middleware: function (connect) {
            //            return [
            //                connect.static('.tmp'),
            //                connect.static('test'),
            //                connect().use(
            //                    '/bower_components',
            //                    connect.static('./bower_components')
            //                ),
            //                connect.static(appConfig.app)
            //            ];
            //        }
            //    }
            //},
            dist: {
                options: {
                    open: true,
                    base: '<%= yeoman.dist %>'
                }
            }
        },

        // Make sure code styles are up to par and there are no obvious mistakes
        jshint: {
            options: {
                jshintrc: '.jshintrc',
                reporter: require('jshint-stylish')
            },
            all: {
                src: [
                    'Gruntfile.js',
                    '<%= yeoman.app %>/scripts/{,*/}*.js'
                ]
            },
            test: {
                options: {
                    jshintrc: 'test/.jshintrc'
                },
                src: ['test/spec/{,*/}*.js']
            }
        },

        tslint: {
            options: {
                configuration: grunt.file.readJSON('tslint.json')
            },
            files: {
                src: ['<%= yeoman.app %>/scripts/**/*.ts']
            }
        },

        // Empties folders to start fresh
        clean: {
            dist: {
                files: [{
                    dot: true,
                    src: [
                        '.tmp',
                        '<%= yeoman.dist %>/{,*/}*',
                        '!<%= yeoman.dist %>/.git{,*/}*',
                        '<%= yeoman.app %>/**/*.js',
                        '<%= yeoman.app %>/**/*.js.map'
                    ]
                }]
            },
            server: '.tmp'
        },

        // Add vendor prefixed styles
        autoprefixer: {
            options: {
                //browsers: ['last 1 version']
                browsers: ['last 3 versions', 'ie 8', 'ie 9', 'ie 10', 'ie 11']
            },
            server: {
                options: {
                    map: true
                },
                files: [{
                    expand: true,
                    cwd: '.tmp/styles/',
                    src: '{,*/}*.css',
                    dest: '.tmp/styles/'
                }]
            },
            dist: {
                files: [{
                    expand: true,
                    cwd: '.tmp/styles/',
                    src: '{,*/}*.css',
                    dest: '.tmp/styles/'
                }]
            }
        },

        // Automatically inject Bower components into the app
        wiredep: {
            app: {
                src: ['<%= yeoman.app %>/index.html'],
                ignorePath: /\.\.\//,
                exclude: [
                    'bower_components/bootstrap-material-design/dist/css/material.css'
                ]
            },
            //test: {
            //    devDependencies: true,
            //    src: '<%= karma.unit.configFile %>',
            //    ignorePath: /\.\.\//,
            //    fileTypes: {
            //        js: {
            //            block: /(([\s\t]*)\/{2}\s*?bower:\s*?(\S*))(\n|\r|.)*?(\/{2}\s*endbower)/gi,
            //            detect: {
            //                js: /'(.*\.js)'/gi
            //            },
            //            replace: {
            //                js: '\'{{filePath}}\','
            //            }
            //        }
            //    }
            //},
            sass: {
                src: ['<%= yeoman.app %>/styles/{,*/}*.{scss,sass}'],
                ignorePath: /(\.\.\/){1,2}bower_components\//,
                fileTypes: {
                    scss: {
                        replace: {
                            css: '@import "../../bower_components/{{filePath}}";',
                            sass: '@import "../../bower_components/{{filePath}}";',
                            scss: '@import "../../bower_components/{{filePath}}";'
                        }
                    }
                }
            },
            less: {
                src: ['<%= yeoman.app %>/styles/{,*/}*.less'],
                ignorePath: /(\.\.\/){1,2}bower_components\//
            }
        },

        injector: {
            options: {},
            tsd: {
                options: {
                    starttag: '// injector:ts',
                    endtag: '// endinjector',
                    transform: function (file, i, length) {
                        if (file.search('.d.ts') === -1) {
                            return "/// <reference path='" + file.replace('/app/scripts/', '') + "' />";
                        }
                    }
                },
                files: {
                    '<%= yeoman.app %>/scripts/all.d.ts': ['<%= yeoman.app %>/scripts/**/*.ts']
                }
            },
            js: {
                options: {
                    starttag: '<!-- build:js({.tmp,app}) scripts/scripts.js -->',
                    endtag: '<!-- endbuild -->',
                    sort: function (a, b) {
                        var va = a.search('.module.ts') === -1 ? 0 : 100;
                        var vb = b.search('.module.ts') === -1 ? 0 : 100;
                        va -= a.split('/').length;
                        vb -= b.split('/').length;
                        return vb - va;
                    },
                    transform: function (file, i, length) {
                        if (file.search('.d.ts') === -1) {
                            file = file.replace('/app/', '').replace('.ts', '.js');
                            return '<script src="' + file + '"></script>';
                        }
                    }
                },
                files: {
                    '<%= yeoman.app %>/index.html': ['<%= yeoman.app %>/scripts/**/*.ts']
                }
            }
            //jstest: {
            //    options: {
            //        starttag: '// injector:js',
            //        endtag: '// endinjector',
            //        sort: function (a, b) {
            //            var va = a.search('.module.ts') === -1 ? 0 : 100;
            //            var vb = b.search('.module.ts') === -1 ? 0 : 100;
            //            va -= a.split('/').length;
            //            vb -= b.split('/').length;
            //            return vb - va;
            //        },
            //        transform: function (file, i, length) {
            //            if (file.search('.d.ts') === -1) {
            //                file = file.replace('/app/', 'app/').replace('.ts', '.js');
            //                return "'" + file + "',";
            //            }
            //        }
            //    },
            //    files: {
            //        'test/karma.conf.js': ['<%= yeoman.app %>/scripts/**/*.ts']
            //    }
            //}
        },

        // Compiles Sass to CSS and generates necessary files if requested
        compass: {
            options: {
                sassDir: '<%= yeoman.app %>/styles',
                cssDir: '.tmp/styles',
                generatedImagesDir: '.tmp/images/generated',
                imagesDir: '<%= yeoman.app %>/images',
                javascriptsDir: '<%= yeoman.app %>/scripts',
                fontsDir: '<%= yeoman.app %>/styles/fonts',
                //importPath: './bower_components',
                httpImagesPath: '/images',
                httpGeneratedImagesPath: '/images/generated',
                httpFontsPath: '/styles/fonts',
                relativeAssets: false,
                assetCacheBuster: false,
                raw: 'Sass::Script::Number.precision = 10\n'
            },
            dist: {
                options: {
                    generatedImagesDir: '<%= yeoman.dist %>/images/generated'
                }
            },
            server: {
                options: {
                    sourcemap: true
                }
            }
        },

        // Compiles LESS to CSS and generates necessary files if requested
        less: {
            options: {
                paths: ['./bower_components'],
            },
            dist: {
                options: {
                    cleancss: true,
                    report: 'gzip'
                },
                files: [{
                    expand: true,
                    cwd: '<%= yeoman.app %>/styles',
                    src: '*.less',
                    dest: '.tmp/styles',
                    ext: '.css'
                }]
            },
            server: {
                options: {
                    sourceMap: true,
                    sourceMapBasepath: '<%= yeoman.app %>/',
                    sourceMapRootpath: '../'
                },
                files: [{
                    expand: true,
                    cwd: '<%= yeoman.app %>/styles',
                    src: '*.less',
                    dest: '.tmp/styles',
                    ext: '.css'
                }]
            }
        },

        // Renames files for browser caching purposes
        filerev: {
            dist: {
                src: [
                    '<%= yeoman.dist %>/scripts/{,*/}*.js',
                    '<%= yeoman.dist %>/styles/{,*/}*.css',
                    '<%= yeoman.dist %>/images/{,*/}*.{png,jpg,jpeg,gif,webp,svg}',
                    '<%= yeoman.dist %>/styles/fonts/*'
                ]
            }
        },

        // Reads HTML for usemin blocks to enable smart builds that automatically
        // concat, minify and revision files. Creates configurations in memory so
        // additional tasks can operate on them
        useminPrepare: {
            html: '<%= yeoman.app %>/index.html',
            options: {
                dest: '<%= yeoman.dist %>',
                flow: {
                    html: {
                        steps: {
                            js: ['concat', 'uglifyjs'],
                            css: ['cssmin']
                        },
                        post: {}
                    }
                }
            }
        },

        // Performs rewrites based on filerev and the useminPrepare configuration
        usemin: {
            html: ['<%= yeoman.dist %>/{,*/}*.html'],
            css: ['<%= yeoman.dist %>/styles/{,*/}*.css'],
            options: {
                assetsDirs: [
                    '<%= yeoman.dist %>',
                    '<%= yeoman.dist %>/images',
                    '<%= yeoman.dist %>/styles'
                ]
            }
        },

        // The following *-min tasks will produce minified files in the dist folder
        // By default, your `index.html`'s <!-- Usemin block --> will take care of
        // minification. These next options are pre-configured if you do not wish
        // to use the Usemin blocks.
        // cssmin: {
        //   dist: {
        //     files: {
        //       '<%= yeoman.dist %>/styles/main.css': [
        //         '.tmp/styles/{,*/}*.css'
        //       ]
        //     }
        //   }
        // },
        // uglify: {
        //   dist: {
        //     files: {
        //       '<%= yeoman.dist %>/scripts/scripts.js': [
        //         '<%= yeoman.dist %>/scripts/scripts.js'
        //       ]
        //     }
        //   }
        // },
        // concat: {
        //   dist: {}
        // },

        imagemin: {
            dist: {
                files: [{
                    expand: true,
                    cwd: '<%= yeoman.app %>/images',
                    src: '{,*/}*.{png,jpg,jpeg,gif}',
                    dest: '<%= yeoman.dist %>/images'
                }]
            }
        },

        svgmin: {
            dist: {
                files: [{
                    expand: true,
                    cwd: '<%= yeoman.app %>/images',
                    src: '{,*/}*.svg',
                    dest: '<%= yeoman.dist %>/images'
                }]
            }
        },

        htmlmin: {
            dist: {
                options: {
                    collapseWhitespace: true,
                    conservativeCollapse: true,
                    // https://github.com/esvit/ng-table/issues/230
                    collapseBooleanAttributes: false,
                    removeCommentsFromCDATA: true,
                    removeOptionalTags: true
                },
                files: [{
                    expand: true,
                    cwd: '<%= yeoman.dist %>',
                    src: ['*.html', 'views/{,*/}*.html'],
                    dest: '<%= yeoman.dist %>'
                }]
            }
        },

        // ng-annotate tries to make the code safe for minification automatically
        // by using the Angular long form for dependency injection.
        ngAnnotate: {
            dist: {
                files: [{
                    expand: true,
                    cwd: '.tmp/concat/scripts',
                    src: '*.js',
                    dest: '.tmp/concat/scripts'
                }]
            }
        },

        // Replace Google CDN references
        cdnify: {
            dist: {
                html: ['<%= yeoman.dist %>/*.html']
            }
        },

        // Copies remaining files to places other tasks can use
        copy: {
            dist: {
                files: [{
                    expand: true,
                    dot: true,
                    cwd: '<%= yeoman.app %>',
                    dest: '<%= yeoman.dist %>',
                    src: [
                        '*.{ico,png,txt}',
                        '.htaccess',
                        '*.html',
                        'views/{,*/}*.html',
                        'images/{,*/}*.{webp}',
                        'styles/fonts/{,*/}*.*'
                    ]
                }, {
                    expand: true,
                    cwd: '.tmp/images',
                    dest: '<%= yeoman.dist %>/images',
                    src: ['generated/*']
                }, {
                    expand: true,
                    cwd: '.',
                    src: 'bower_components/bootstrap-sass-official/assets/fonts/bootstrap/*',
                    dest: '<%= yeoman.dist %>'
                }, {
                    expand: true,
                    cwd: 'bower_components/font-awesome',
                    src: 'fonts/*',
                    dest: '<%= yeoman.dist %>'
                }, {
                    expand: true,
                    cwd: 'bower_components/bootstrap',
                    src: 'fonts/*',
                    dest: '<%= yeoman.dist %>'
                }, {
                    expand: true,
                    cwd: 'bower_components/bootstrap-material-design',
                    src: 'fonts/*',
                    dest: '<%= yeoman.dist %>'
                }]
            },
            styles: {
                expand: true,
                cwd: '<%= yeoman.app %>/styles',
                dest: '.tmp/styles/',
                src: '{,*/}*.css'
            }
        },

        // Run some tasks in parallel to speed up the build process
        concurrent: {
            server: [
                //'compass:server',
                'less:server'
            ],
            //test: [
            //    //'compass',
            //    'less'
            //],
            dist: [
                //'compass:dist',
                'less:dist',
                'copy:styles',
                'imagemin',
                'svgmin'
            ]
        },

        // Test settings
        //karma: {
        //    unit: {
        //        configFile: 'test/karma.conf.js',
        //        singleRun: true
        //    }
        //},

        typescript: {
            base: {
                src: ['<%= yeoman.app %>/**/*.ts'],
                options: {
                    module: 'amd',
                    target: 'es5',
                    basePath: '<%= yeoman.app %>',
                    sourceMap: true,
                    declaration: false
                }
            }
        }
    });


    grunt.registerTask('serve', 'Compile then start a connect web server', function (target) {
        if (target === 'dist') {
            return grunt.task.run(['build', 'connect:dist:keepalive']);
        }

        grunt.task.run([
            'clean:server',
            'wiredep',
            'concurrent:server',
            'autoprefixer:server',
            'connect:livereload',
            'watch'
        ]);
    });

    grunt.registerTask('server', 'DEPRECATED TASK. Use the "serve" task instead', function (target) {
        grunt.log.warn('The `server` task has been deprecated. Use `grunt serve` to start a server.');
        grunt.task.run(['serve:' + target]);
    });

    //grunt.registerTask('test', [
    //    'clean:server',
    //    'wiredep',
    //    'ts',
    //    'concurrent:test',
    //    'autoprefixer',
    //    'connect:test',
    //    'karma'
    //]);

    grunt.registerTask('build', [
        'clean:dist',
        'ts',
        'wiredep',
        'useminPrepare',
        'concurrent:dist',
        'autoprefixer',
        'concat',
        'ngAnnotate',
        'copy:dist',
        //'cdnify',
        'cssmin',
        'uglify',
        'filerev',
        'usemin',
        'htmlmin'
    ]);

    grunt.registerTask('ts', [
        'injector',
        'typescript'
    ]);

    grunt.registerTask('default', [
        // 'newer:jshint', // We use TypeScript
        'ts',
        'tslint',
        // 'test',
        'build'
    ]);
};

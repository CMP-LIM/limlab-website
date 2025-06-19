/**
 * Installation:
 * 1. Install Grunt CLI (`npm install -g grunt-cli`)
 * 1. Install Grunt 0.4.0 and other dependencies (`npm install`)
 *
 * Build:
 * Execute `grunt` from root directory of this directory (where Gruntfile.js is)
 * To execute automatically after each change, execute `grunt --force default watch`
 * To execute build followed by the test run, execute `grunt test`
 *
 * See http://gruntjs.com/getting-started for more information about Grunt
 */
module.exports = function (grunt) {
	grunt.initConfig({
			jade: {
				compileAll: {
					options: {
						pretty: true,
					},
					files: [{
						expand: true,
						src: ["**/*.jade", "!**/_*.jade"], 
						cwd: 'src/',
						ext: ".html",
						dest: 'dest/'
					}]
				}
			},
			
			cssmin: {
				main: {
					expand: true,
					cwd: 'src/css/',
					src: ['*.css', '!*.min.css'],
					dest: 'dest/css/',
					extDot: 'last',
					ext: '.min.css'
				}
			},

			sass: {
				dist: {
					options: {
						implementation: require('sass'),
						sourceMap: true
					},
					files: [{
						src: "*.scss", 
						cwd: "src/sass",
						dest: "dest/css", 
						expand: true,
						ext: ".css"
					}]
				}
			},

			clean: {
				dist: ['tmp']
			},

			connect: {
				dev: {
					options: {
						port: 9000,
						hostname: "0.0.0.0",
						base: "dist",
						keepalive: true
					}
				}
			},
			copy: {
			  main: {
			    files: [
			      // includes files within path
			      {expand: true, 
			       src: ['css/**'], 
			       cwd: 'src/',
			       dest: 'dest/'},
			       {expand: true, 
			       src: ['js/**'], 
			       cwd: 'src/',
			       dest: 'dest/'},
			       {expand: true, 
			       src: ['images/**'], 
			       cwd: 'src/',
			       dest: 'dest/'},
			       {expand: true, 
			       src: ['font/**'], 
			       cwd: 'src/',
			       dest: 'dest/'},
			       {expand: true, 
			       src: ['people/images/**'], 
			       cwd: 'src/',
			       dest: 'dest/'},
			       {expand: true, 
			       src: ['people/portraits/**'], 
			       cwd: 'src/',
			       dest: 'dest/'},
			       {expand: true, 
			       src: ['pdfs/**'], 
			       cwd: 'src/',
			       dest: 'dest/'},
			       {expand: true, 
			       src: ['downloads/**'], 
			       cwd: 'src/',
			       dest: 'dest/'},			    ],
			  },
			},


});

	// DEFAULT TASKS
	grunt.registerTask('default', ['sass', 'jade', 'cssmin', 'copy']);
	grunt.registerTask('build', ['sass', 'jade', 'cssmin', 'clean']);
	grunt.loadNpmTasks('grunt-sass');

	grunt.loadNpmTasks('grunt-replace');
	grunt.loadNpmTasks('grunt-contrib-clean');
	grunt.loadNpmTasks('grunt-contrib-cssmin');
	grunt.loadNpmTasks('grunt-contrib-connect');
	grunt.loadNpmTasks('grunt-contrib-copy');
	grunt.loadNpmTasks('grunt-contrib-uglify');
	grunt.loadNpmTasks('grunt-contrib-jade');
};

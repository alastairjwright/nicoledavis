var gulp = require('gulp');
var plumber = require('gulp-plumber');
var cssGlobbing = require('gulp-css-globbing');
var rename = require('gulp-rename');
var sass = require('gulp-sass');
var autoPrefixer = require('gulp-autoprefixer');
var cssComb = require('gulp-csscomb');
var cmq = require('gulp-combine-media-queries');
var minifyCss = require('gulp-minify-css');
var uglify = require('gulp-uglify');
var concat = require('gulp-concat');
var order = require("gulp-order");
var notify = require('gulp-notify');
var sourcemaps = require('gulp-sourcemaps');
var paths = {
	js: [
    'html/wp-content/themes/nicoledavis/assets/js/lib/*.js',
		'html/wp-content/themes/nicoledavis/assets/js/views/*.js'
	]
};
gulp.task('sass',function(){
	gulp.src(['html/wp-content/themes/nicoledavis/assets/scss/style.scss'])
		.pipe(plumber({
			handleError: function (err) {
				console.log(err);
				this.emit('end');
			}
		}))
		// .pipe(sourcemaps.init())
		.pipe(cssGlobbing({ extensions: ['.scss'] }))
		.pipe(sass())
		.pipe(autoPrefixer({'browsers': ['last 2 versions', 'Safari >= 8']}))
		.pipe(cssComb())
		.pipe(concat('style.css'))
		.pipe(minifyCss())
		// .pipe(sourcemaps.write('./'))
		.pipe(gulp.dest('html/wp-content/themes/nicoledavis'))
		.pipe(notify('css task finished'));
});
gulp.task('js',function(){
	gulp.src(paths.js)
		.pipe(plumber({
			handleError: function (err) {
				console.log(err);
				this.emit('end');
			}
		}))
		.pipe(sourcemaps.init())
		.pipe(order([
			'html/wp-content/themes/nicoledavis/assets/js/lib/*.js',
			'html/wp-content/themes/nicoledavis/assets/js/views/*.js'
		], { base: './' }))
		.pipe(concat('app.min.js'))
		.pipe(uglify())
		.pipe(sourcemaps.write('./'))
		.pipe(gulp.dest('html/wp-content/themes/nicoledavis/assets/js/min'))
		.pipe(notify('js task finished'));
});
gulp.task('watch',function(){
	gulp.watch(paths.js,['js']);
	gulp.watch('html/wp-content/themes/nicoledavis/assets/scss/**/*.scss',['sass']);
});
gulp.task('default',['sass','js']);

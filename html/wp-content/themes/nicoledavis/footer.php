<?php
/**
 * The template for displaying the footer
 *
 * Contains the closing of the #content div and all content after.
 *
 * @link https://developer.wordpress.org/themes/basics/template-files/#template-partials
 *
 * @package nicoledavis
 */

?>

	</div><!-- #content -->

	<footer class="site-footer">
		<a href="mailto:<?php the_field('footer_email', 'option'); ?>"><?php the_field('footer_text', 'option'); ?></a>
	</footer><!-- #colophon -->
</div><!-- #page -->

<script type="text/javascript" src="<?php echo get_template_directory_uri().'/assets/js/min/app.min.js'; ?>"></script>
<?php wp_footer(); ?>

</body>
</html>

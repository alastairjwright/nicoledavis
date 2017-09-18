<?php
/**
 * Template Name: About
 */
?>
<?php get_header(); ?>
	<div id="primary" class="content-area">
		<main id="main" class="work-grid">

			<?php while ( have_posts() ) : the_post(); ?>

				<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>

					<div class="entry-content">
						<div class="entry-copy">
							<div class="entry-description">
								<?php the_content(); ?>
							</div>
							<div class="entry-list">
								<?php the_field('list'); ?>
							</div>
						</div>
					</div><!-- .entry-content -->

				</article><!-- #post-<?php the_ID(); ?> -->

			<?php endwhile; ?>

		</main><!-- #main -->
	</div><!-- #primary -->

<?php get_footer(); ?>

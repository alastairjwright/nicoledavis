<?php get_header(); ?>
	<div id="primary" class="content-area">
		<main id="main" class="site-main">

		<?php while ( have_posts() ) : the_post(); ?>

			<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>

				<div class="entry-content">
					<div class="entry-hero">
						<?php the_post_thumbnail(); ?>
					</div>
					<div class="entry-copy">
						<div class="entry-description">
							<?php the_content(); ?>
						</div>
						<div class="entry-list">
							<?php the_field('list'); ?>
						</div>
					</div>

					<div class="entry-gallery">
						<?php

						$images = get_field('project_images');
						$size = 'full'; // (thumbnail, medium, large, full or custom size)

						if( $images ): ?>
							<?php foreach( $images as $image ): ?>
								<?php echo wp_get_attachment_image( $image['ID'], $size ); ?>
							<?php endforeach; ?>
						<?php endif; ?>
					</div>

					<div class="entry-grid">

					</div>
				</div><!-- .entry-content -->

			</article><!-- #post-<?php the_ID(); ?> -->

		<?php endwhile; ?>

		</main><!-- #main -->
	</div><!-- #primary -->

<?php get_footer(); ?>

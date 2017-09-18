<?php

$posts = get_field('work_posts', 5);

if( $posts ): ?>

	<?php foreach( $posts as $post): // variable must be called $post (IMPORTANT) ?>
		<?php setup_postdata($post); ?>

		<?php
			$size = get_field('home_page_size');
			if ($size == 'small') {
				$image = get_field('small_home_page_image');
			}

			if ($size == 'medium') {
				$image = get_field('medium_home_page_image');
			}

			$categories = get_the_category();
		?>

		<article id="post-<?php the_ID(); ?>" <?php post_class(array('work-item', 'work-item-'.$size)); ?>>

			<a href="<?php echo esc_url( get_permalink() ); ?>">

				<img srcset="<?php the_post_thumbnail_url()?> 640w, <?php echo $image['url'];?> 641w" alt="<?php echo $image['alt'];?>">

				<div class="grid-bg-image" style="background-image: url(<?php echo $image['url'];?>)"></div>

				<div class="work-info">
					<h2><?php echo $categories[0]->name; ?></h2>
					<?php the_title( '<h1 class="entry-title">', '</h1>' ); ?>
				</div>
			</a>

		</article><!-- #post-<?php the_ID(); ?> -->

	<?php endforeach; ?>

	<?php wp_reset_postdata(); // IMPORTANT - reset the $post object so the rest of the page works correctly ?>
<?php endif; ?>

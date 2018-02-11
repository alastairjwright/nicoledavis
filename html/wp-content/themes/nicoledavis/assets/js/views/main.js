var DS = DS || {};
(function($){
    var scrollTop;
    var windowHeight;

     $(window).scroll(function() {

        scrollTop = $(window).scrollTop();
        windowHeight = $(window).height();

        $('video').each(function(){
            var videoTop = $(this).offset().top;
            var videoHeight = $(this).height();

            if ((scrollTop + windowHeight) > videoTop && !$(this).hasClass('pause') && !$(this).hasClass('scrolledPast')) {
                $(this).addClass('scrolledTo');
                $(this)[0].play();
            } else {
                $(this).removeClass('scrolledTo');
                $(this)[0].pause();
            }

            if (scrollTop > (videoTop + videoHeight)) {
                $(this).addClass('scrolledPast');
                $(this)[0].pause();
            } else {
                $(this).removeClass('scrolledPast');
            }
        })
    });

     $('video').on('click', function () {
        if ($(this)[0].paused == false) {
              $(this)[0].pause();
              $(this).addClass('pause');
          } else {
              $(this)[0].play();
              $(this).removeClass('pause');
          }
     })

     $(window).trigger('scroll');
}(jQuery));

<script>
  var isNavVisible = true;

  $(document).ready(function () {
    // Handle swipe up and down events
    var startY = 0;
    var endY = 0;

    $(document).on('touchstart', function (e) {
      startY = e.originalEvent.touches[0].pageY;
    });

    $(document).on('touchend', function (e) {
      endY = e.originalEvent.changedTouches[0].pageY;

      // Swipe up
      if (startY > endY && isNavVisible) {
        $('.bottom-nav').css('transform', 'translateY(100%)');
        $('.bottom-nav').css('opacity', '0');
        isNavVisible = false;
      }
      // Swipe down
      else if (startY < endY && !isNavVisible) {
        $('.bottom-nav').css('transform', 'translateY(0)');
        $('.bottom-nav').css('opacity', '1');
        isNavVisible = true;
      }
    });
  });
</script>

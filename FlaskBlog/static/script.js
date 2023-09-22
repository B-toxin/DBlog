var swiper = new Swiper('.swiper-container', {
  slidesPerView: 1,
  spaceBetween: 20,
  effect: 'fade',
  loop: true,
  speed: 300,
  mousewheel: {
    invert: false,
  },
  pagination: {
    el: '.swiper-pagination',
    clickable: true,
    dynamicBullets: true
  },
  autoplay: {
    delay: 3000, // Time in milliseconds between slides
    disableOnInteraction: false, // Prevent autoplay from stopping when user interacts with the slider
  }
});

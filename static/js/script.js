

  $(document).ready(function(){
    $('.slider').slider({
      fullWidth: true,
      originalWidth: '100%',
      indicators: false,
      interval: 3000
    });
    $('select').formSelect();
    $('.sidenav').sidenav();
    $('.collapsible').collapsible();
  });
        

  $('.carousel-slider').carousel({fullWidth: true, padding:0},setTimeout(autoplay, 4500));
  function autoplay() {
    $('.carousel').carousel('next');
    setTimeout(autoplay, 7500);
     }
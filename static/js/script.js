

  $(document).ready(function(){
    $('.slider').slider({
      full_width: true,
      originalWidth: '100%',
      indicators: false,
      interval: 3000
    });
    $('select').formSelect();
    $('.sidenav').sidenav();
    $('.collapsible').collapsible();
  });
        
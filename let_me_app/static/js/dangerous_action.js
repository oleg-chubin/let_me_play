$(function(){
    $('.container').on('click', 'button[data-confirmation]', function(){
       if (confirm($(this).data('confirmation'))) {
           return true;
       } else {
           return false;
       }
    });
})

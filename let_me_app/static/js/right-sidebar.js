$(function() {
    $('sidebar, .nav-controller').on('click', function(event) {
        $('sidebar').toggleClass('focus');
    });
    $('sidebar, .nav-controller').on('mouseover', function(event) {
        $('sidebar').addClass('focus');
    }).on('mouseout', function(event) {
        $('sidebar').removeClass('focus');
    })
})

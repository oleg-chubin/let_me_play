$(document).ready(function() {
    $('[id^=detail-]').hide();
    $('.toggle').click(function() {
        $input = $(this);
        $target = $('#'+$input.data('toggle'));
        $target.slideToggle();
        $icon = $input.find('span.toggle-icon').toggle()
    });
});

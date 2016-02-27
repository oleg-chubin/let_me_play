$(document).ready(function(e){
    $("form .img-check").map(
        function(){
            var self = $(this)
            var checkbox = self.closest('li').find('input[type=checkbox]');
            checkbox.addClass('hidden');
            if (checkbox.is(':checked')) self.removeClass('uncheck');
        }
    );
    $("form").off('click', ".img-check").on('click', ".img-check", function(e){
        $(this).toggleClass("uncheck");
        e.handled = true;
    });
});

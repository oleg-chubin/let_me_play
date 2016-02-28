window.onFormWithRadioLoad = function(form){
    form.find('.img-check').map(
        function(){
            var self = $(this)
            var checkbox = self.find('input[type=radio]');
            checkbox.addClass('hidden');
            if (checkbox.is(':checked')) self.removeClass('uncheck');
        }
    );
    form.off('click', ".img-check").on('click', ".img-check", function(e){
        var self = $(this);
        if (self.find('input[type=radio]')) {
            self.closest('form').find(".img-check").addClass("uncheck");
            self.removeClass("uncheck");
        }
    });
}

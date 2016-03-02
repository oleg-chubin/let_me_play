$(function(){
    $('a[data-toggle="modal"]').click(
        function(){
            var self = $(this);
            var generation_url = self.data('generateurl');
            var confirmation_url = self.data('confirmurl');
            var form_data = $(self.data('target')).find('form').serialize();
            $(self.data('target')).find('form').attr('action', self.data('formurl'));
            $.post(generation_url, form_data, function(){
            });
        }
    );
})

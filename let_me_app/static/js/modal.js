$(function(){
    $('a[data-toggle="modal"]').click(
        function(){
            self = $(this);
            $(self.data('target')).find('form').attr('action', self.data('formurl'));
        }
    );
})

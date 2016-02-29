$(function(){
    $('[data-toggle="popover"]').popover({
        html: true,
        content: function(e){
            var url = $(this).data('popover_url');
            var content = '<div class="popo><img src="/static/images/ajax-loader-small.gif"></div>';
            var self = $(this);
            $.get(url, function(data){
                var remote_content = $(data).find('.content');
                remote_content.find('.form-group').removeClass('form-group');
                remote_content.find('button[type=submit]').remove();
                var popover = $('#'+self.attr('aria-describedby'));
                remote_content.find('input[type=radio]').change(function(){
                    var form = $(this).closest('form');
                    $.ajax({
                        type: "POST",
                        url: form.attr('action'),
                        data: form.serialize()
                    });
                    $(self).popover('hide');
                });
                window.onFormWithRadioLoad(remote_content.find('form'));

                var position = popover.position();
                var previous_height = popover.height();
                popover.find('.popover-content').html(remote_content);
                var height = popover.height();
                var adjustment = (height - previous_height)/2;
                popover.css({ top: position.top - adjustment });
            });
            return content;
        }
    });
})

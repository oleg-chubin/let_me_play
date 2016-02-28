$(function(){
    $('[data-toggle="popover"]').popover({
        html: true,
        content: function(e){
            var url = $(this).data('popover_url');
            var content = $('<div><img src="/static/images/ajax-loader-small.gif"></div>');
            $.get(url, function(data){
                var remote_content = $(data).find('.content');
                remote_content.find('.form-group').removeClass('form-group');
                remote_content.find('button[type=submit]').remove();
                remote_content.find('input[type=radio]').change(function(){
                    var form = $(this).closest('form');
                    $.ajax({
                        type: "POST",
                        url: form.attr('action'),
                        data: form.serialize()
                    });
                    content.closest('.popover').popover('hide');
                });
                content.html(remote_content);
                window.onFormWithRadioLoad(remote_content.find('form'));

            });
            return content;
        }
    });
})

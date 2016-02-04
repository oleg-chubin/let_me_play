
$(function() {
    var chat_container = $('.chat-container');
    var chat_controller = $('<div class="chat-controller"></div>');
    chat_controller.append('<span class=" glyphicon glyphicon-envelope controller-open"></span>');
    chat_controller.append('<span class=" glyphicon glyphicon-remove controller-close"></span>');

    $('body').append(chat_controller);

    var li_count = null;

    chat_controller.on('click', function(event) {
        $('.chat-container').toggleClass('focus');
        if ($('.chat-container').hasClass('focus')){
            chat_controller.find('span.glyphicon-envelope').removeClass('new-messages');
        }
    });

    var pannel_body = $('<div class="panel-body"></div>');
    chat_container.append(pannel_body);
    pannel_footer = $(' <div class="panel-footer"></div>');
    chat_container.append(pannel_footer);

    var chat_url = $('.chat-container').data('chaturl');
    var post_chat_url = $('.chat-container').data('postchaturl');

    function update_chat_pannel(data){
        pannel_body.children().remove();
        pannel_body.append($(data).find('.panel-body .chat'));

        var li_number = pannel_body.find('li').length;
        if (li_count && li_count<li_number){
            if (!$('.chat-container').hasClass('focus')){
                chat_controller.find('span.glyphicon-envelope').addClass('new-messages');
            }
        }
        li_count = li_number;

        pannel_footer.children().remove();
        pannel_footer.append($(data).find('.panel-footer form'));
        pannel_body.animate({
            scrollTop: pannel_body[0].scrollHeight
        }, 500);
        setTimeout($.get, 60000, chat_url, update_chat_pannel);
    }

    $.get(chat_url, update_chat_pannel);

    $('.panel-footer').on('click', '#btn-chat', function(){
        $.post(
            post_chat_url,
            $('.panel-footer form').serialize(),
            update_chat_pannel
        )
        return false;
    });

})

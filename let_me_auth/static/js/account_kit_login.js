AccountKit_OnInteractive = function(){
    var login_span = $('.login-link');
    var csrf_token = login_span.find('[name="csrf_token"]').val(),
        facebook_app_id = login_span.find('[name="facebook_app_id"]').val();
    console.log(csrf_token);
    AccountKit.init(
        {
          appId: facebook_app_id,
          state: csrf_token,
          version:"v1.0",
          debug: true
        }
    );
    login_span.removeClass('disabled');
};

function do_after_login(perform_action){
    function perform_auth_step (data, textStatus, request){
      if (request.getResponseHeader('Authentification-Scope') != 'True'){
          var response_parsed = $(request.responseText);
          $('.navbar-fixed-top').replaceWith(response_parsed.filter('.navbar-fixed-top'));
          $('input[name="csrfmiddlewaretoken"]').val(response_parsed.find('input[name="csrfmiddlewaretoken"]').val());
          perform_action();
      }
      else{
          var content = $(data).find('.content'),
              modal = $('#authModal');
          modal.find('.modal-title').html(content.find('.for-modal-header').html());
          var new_modal_body = content.find('.for-modal-body'),
              old_modal_body = modal.find('.modal-body');
          old_modal_body.html('');
          old_modal_body.append(new_modal_body);
          new_modal_body.map(function(data){
              var form = $(this);
              form.submit(function( event ) {
                  // Stop form from submitting normally
                  event.preventDefault();
                  $.post(form.attr('action'), form.serialize(), perform_auth_step);
                  $('#authModal').modal('hide');
              });
          });
          modal.find('.modal-footer').html('')
          modal.find('.modal-footer').append(content.find('.for-modal-footer'));
          $('#authModal').modal('show');
      }
    }
    return perform_auth_step
}

function getCustomLoginCallback(actionPerformer){
    return function (response) {
        if (response.status === "PARTIALLY_AUTHENTICATED") {
          var data_to_send = {
            code: response.code, csrfmiddlewaretoken: response.state
          };
          var url = $('.login-link').attr('href');
          $.post(
              url,
              data_to_send,
              do_after_login(actionPerformer)
          );
        }
        else if (response.status === "NOT_AUTHENTICATED") {
          // handle authentication failure
        }
        else if (response.status === "BAD_PARAMS") {
          // handle bad parameters
        }
    }
}


$(function(){
    var script = document.createElement('script');
    script.onload = function () {
        //do stuff with the script
//         AccountKit_OnInteractive();

      $('.after-login[type="submit"]').closest('form').submit(function(event){
          var user_profile = $('.navbar-fixed-top a.profile');
          if (user_profile.length > 0) return true;

          var self = $(this);
          event.preventDefault();
          AccountKit.login(
            'PHONE', {'countryCode': '+375'}, getCustomLoginCallback(function(){self.submit();}));
          return false;
      });

      $('a.after-login').click(function(event){
          var user_profile = $('.navbar-fixed-top a.profile');
          if (user_profile.length > 0) return true;

          var final_location = $(this).attr('href');
          event.preventDefault();
          AccountKit.login(
            'PHONE', {'countryCode': '+375'}, getCustomLoginCallback(function(){document.location=final_location}));
          return false;
      });

      $(".login-link").on('click', function(event) {
        var final_location = $(this).attr('href');
        event.preventDefault();
        AccountKit.login(
            'PHONE',
            {'countryCode': '+375'},
            getCustomLoginCallback(
                function(){
                    document.location = final_location;
                }
            )
        );
      });

    };
    script.src = "https://sdk.accountkit.com/ru_RU/sdk.js";
    document.head.appendChild(script);
})



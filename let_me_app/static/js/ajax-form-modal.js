$(function(){
    $('.ajax-form-modal').on('show.bs.modal', function(){
      var form_self = $(this).find('form');
      var form_url = form_self.attr('action');
      $.get(form_url, function(data){
          remote_content = $(data).find('.content form');
          remote_content.find('button[type="submit"]').remove();
          form_self.find('.form-content').html(remote_content.html())

          form_self.submit(function(){
            var form = $(this);
            $.ajax({
                type: "POST", url: form.attr('action'), data: form.serialize()
            });
            document.location = document.location;
            return false;
          });
      });

    });
    $('.ajax-form-modal').on('hidden.bs.modal', function(){
        $(this).find('form .form-content').html('');
    });
})

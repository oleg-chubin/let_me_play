$(document).on('click', '#close-preview', function(){
    // Hover befor close the preview
    $(this).closest('.form-group').find('.image-preview').hover(
        function () {
           $(this).popover('show');
        },
         function () {
           $(this).popover('hide');
        }
    );
    $(this).closest('.popover').popover('hide');
});

$(function() {
    // Create the close button
    var closebtn = $('<button/>', {
        type:"button",
        text: 'x',
        id: 'close-preview',
        style: 'font-size: initial;',
    });
    closebtn.attr("class","close pull-right");
    // Set the popover default content
    $('.image-preview').popover({
        trigger:'manual',
        html:true,
        title: "<strong>Preview</strong>"+$(closebtn)[0].outerHTML,
        content: "There's no image",
        placement:'bottom'
    });
    $('.image-preview[data-content]').popover('show');
    // Clear event
    $('.image-preview-clear').click(function(){
        var image_preview = $(this).closest('.image-preview');
        image_preview.attr("data-content","").popover('hide');
        image_preview.find('.image-preview-filename').val("");
        image_preview.find('.image-preview-clear').hide();
        image_preview.find('.image-preview-input input:file').val("");
        image_preview.find(".image-preview-input-title").text("Browse");
    });
    // Create the preview image
    $(".image-preview-input input:file").change(function (){
        var img = $('<img/>', {
            id: 'dynamic',
            width:250,
            height:200
        });
        var file = this.files[0];
        var reader = new FileReader();
        var self_preview = $(this).closest('.image-preview');
        // Set preview image into the popover data-content
        reader.onload = function (e) {
            self_preview.find(".image-preview-input-title").text("Change");
            self_preview.find(".image-preview-clear").show();
            self_preview.find(".image-preview-filename").val(file.name);
            img.attr('src', e.target.result);
            self_preview.attr("data-content", $(img)[0].outerHTML).popover("show");
        }
        reader.readAsDataURL(file);
    });
});
